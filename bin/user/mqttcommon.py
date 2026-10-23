#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
""" Common code for the weewx-mqtt extensions. """
import abc
import logging
import ssl
import threading
import time

import configobj
import paho.mqtt.client as mqtt

# The mqttcommon API level. Bump it when a change requires consumers to have a newer
# copy than older extensions ship (new shared functions, etc). Each consumer verifies
# at import that the loaded copy meets its required level, so a stale copy - an
# install-order overwrite - fails loudly instead of with a mysterious error later.
MQTTCOMMON_API = (1, 0)

API_V1 = 'v1'
API_V2_MQTT3 = 'v2-mqtt3'
API_V2_MQTT5 = 'v2-mqtt5'

MQTT3_PROTOCOLS = (mqtt.MQTTv31, mqtt.MQTTv311)

PAHO_LOG_LEVELS = {
    mqtt.MQTT_LOG_INFO: 'INFO',
    mqtt.MQTT_LOG_NOTICE: 'INFO',
    mqtt.MQTT_LOG_WARNING: 'INFO',
    mqtt.MQTT_LOG_ERR: 'ERROR',
    mqtt.MQTT_LOG_DEBUG: 'DEBUG'
}

# Some versions of these constants are dependent on the OpenSSL install,
# so only the ones that are available can be used. The legacy protocols are
# only reached when a user explicitly configures 'tls_version' for an old
# broker. The default is 'tlsv12'.
SSL_PROTOCOLS = (
    ('tls', 'PROTOCOL_TLS'),
    ('tlsv1', 'PROTOCOL_TLSv1'),
    ('tlsv11', 'PROTOCOL_TLSv1_1'),
    ('tlsv12', 'PROTOCOL_TLSv1_2'),
    ('sslv2', 'PROTOCOL_SSLv2'),
    ('sslv23', 'PROTOCOL_SSLv23'),
    ('sslv3', 'PROTOCOL_SSLv3')
)


class QueueLoggerThread(threading.Thread, abc.ABC):
    """ Drain a log queue and hand the entries to the concrete logger.

        The queue loop, the daemon flag, and the thread rename are shared so they
        cannot drift between the extensions; the entry format and the start, exit,
        and invalid entries are the concrete class's responsibility. The hooks are
        invoked from the thread itself, so entries may use the thread's name and
        native id. """

    def __init__(self, log_queue, logger):
        threading.Thread.__init__(self)
        self.daemon = True
        self.log_queue = log_queue
        self.logger = logger

    def run(self):
        """ Log the start entry, then the queued entries until the None sentinel arrives. """
        threading.current_thread().name = f"{self.__class__.__name__}-{threading.get_native_id()}"
        self.logger.log_entry(self.start_entry())

        while True:
            entry = self.log_queue.get()
            if entry is None:
                break
            try:
                self.logger.log_entry(entry)
            except (TypeError, KeyError):
                self.logger.log_entry(self.invalid_entry(entry))

        self.logger.log_entry(self.exit_entry())

    @abc.abstractmethod
    def start_entry(self):
        """ Return the entry logged when the thread starts. """

    @abc.abstractmethod
    def exit_entry(self):
        """ Return the entry logged when the thread exits. """

    @abc.abstractmethod
    def invalid_entry(self, entry):
        """ Return the error entry logged for an entry that could not be logged. """


class Logger:
    """ Manage the logging.
        The log queue and the LoggerThread that drains it are owned here.

        The message format is shared; what the format's first argument is is
        the hook: subclasses pin LOG_KEY or override _format_args. The entry
        contract, throttling, the thread class, and the logger itself are the
        other hooks: is_suppressed, stuck_entry, and the thread_class/log ctor
        arguments. """
    # The default time shutdown waits for the LoggerThread to flush queued messages.
    SHUTDOWN_TIMEOUT = 10

    # The name of the module logger, the message format, and the context key.
    # LOG_KEY names the entry field used as the format's first argument; subclasses
    # may instead override _format_args to compose it.
    LOG_NAME = __name__
    LOG_FORMAT = "(%s) %s"
    LOG_KEY = 'name'

    def __init__(self, name, log_queue, thread_class=None, log=None):
        self.name = name
        # A subclass that already configured its logger (before its thread starts) passes it in.
        self.log = log if log is not None else logging.getLogger(self.LOG_NAME)
        self.log_queue = log_queue
        self.log_functions = {
            'TRACE': self._log_trace,
            'DEBUG': self._log_debug,
            'INFO': self._log_info,
            'ERROR': self._log_error,
        }
        # thread_class lets a subclass drain with its own LoggerThread (its entry texts).
        self.log_thread = (thread_class or LoggerThread)(self.log_queue, self)
        self.log_thread.start()

    @staticmethod
    def create_entry(name, log_type, msg_id, msg_text):
        """ Create a log entry, capturing the emitting thread. """
        return {
            'name': name,
            'log_type': log_type,
            'msg_id': msg_id,
            'msg_text': msg_text,
            'thread_id': threading.get_native_id(),
        }

    def trace(self, msg_id, msg_text):
        """ Queue a trace message. """
        self.log_queue.put(Logger.create_entry(self.name, 'TRACE', msg_id, msg_text))

    def debug(self, msg_id, msg_text):
        """ Queue a debug message. """
        self.log_queue.put(Logger.create_entry(self.name, 'DEBUG', msg_id, msg_text))

    def info(self, msg_id, msg_text):
        """ Queue an informational message. """
        self.log_queue.put(Logger.create_entry(self.name, 'INFO', msg_id, msg_text))

    def error(self, msg_id, msg_text):
        """ Queue an error message. """
        self.log_queue.put(Logger.create_entry(self.name, 'ERROR', msg_id, msg_text))

    def log_entry(self, entry):
        """ Log a queued entry. This is called by the LoggerThread. """
        if not self.is_suppressed(entry):
            self.log_functions[entry['log_type']](entry)

    def is_suppressed(self, entry):
        """ Return True when the entry should not be logged. """
        return entry['log_type'] is None

    def shutdown(self, timeout=SHUTDOWN_TIMEOUT):
        """ Stop the logger thread, flushing queued messages. """
        if not self.log_thread.is_alive():
            return

        self.log_queue.put(None)
        self.log_thread.join(timeout)
        if self.log_thread.is_alive():
            # The thread is stuck, a queued message would not be logged so log it directly.
            self._log_error(self.stuck_entry())

    def stuck_entry(self):
        """ Return the entry logged when the logger thread is stuck in shutdown. """
        return Logger.create_entry(self.name, 'ERROR', None,
                                   f"Unable to shut down {self.log_thread.name} thread")

    def _format_args(self, entry):
        """ Return the format arguments for an entry; the message is always last. """
        return (entry[self.LOG_KEY], entry['msg_text'])

    def _log_trace(self, entry):
        """ Log a trace entry. This is called by the LoggerThread. """
        self.log.debug(self.LOG_FORMAT, *self._format_args(entry))

    def _log_debug(self, entry):
        """ Log a debug entry. This is called by the LoggerThread. """
        self.log.debug(self.LOG_FORMAT, *self._format_args(entry))

    def _log_info(self, entry):
        """ Log an informational entry. This is called by the LoggerThread. """
        self.log.info(self.LOG_FORMAT, *self._format_args(entry))

    def _log_error(self, entry):
        """ Log an error entry. This is called by the LoggerThread. """
        self.log.error(self.LOG_FORMAT, *self._format_args(entry))


class LoggerThread(QueueLoggerThread):
    """ Thread to manage logging.
        This has to be a thread because WeeWX 'owns' the logger.
        So logging has to happen in that process and not a subprocess.
        The queue loop is inherited from QueueLoggerThread. """

    def start_entry(self):
        """ Return the entry logged when the thread starts. """
        return Logger.create_entry(self.name, 'INFO', None, "Starting logger thread")

    def exit_entry(self):
        """ Return the entry logged when the thread exits. """
        return Logger.create_entry(self.name, 'INFO', None, f"Exited logger thread, {self.name}.")

    def invalid_entry(self, entry):
        """ Return the error entry logged for an entry that could not be logged. """
        return Logger.create_entry(self.name, 'ERROR', None, entry)


# These mirror weeutil.weeutil.to_int/option_as_list so that mqttcommon stays importable
# without weewx (subscribe's unit suite stubs weewx and has no weeutil).
def _to_int(x):
    if isinstance(x, str) and (x.lower() == 'none' or x == ''):
        x = None
    try:
        return int(x) if x is not None else None
    except ValueError:
        # Perhaps it's a string, holding a floating point number?
        return int(float(x))


def _as_list(option):
    if option is None:
        return None
    return [option] if not isinstance(option, list) else option


class MessageThrottle:  # pylint: disable=too-few-public-methods
    """ Decide whether a log message must be suppressed.

    Messages are throttled by key (typically a message id), falling back to the
    log type's category and then to 'ALL'. Key None messages are never throttled.

    The throttle state is only ever accessed from the logger thread, so no
    locking is needed. Summaries of suppressed messages are passed to the
    optional log_summary callback, which the consumer wires to its logger. """

    VALID_CATEGORIES = ['ALL', 'ERROR', 'INFO', 'DEBUG', 'TRACE']

    # The suppression summaries, formatted and passed to the log_summary callback.
    SUMMARY_WINDOW = "{count} messages have been suppressed in window id: {window}."
    SUMMARY_DURATION_ZERO = "{count} messages have been suppressed of {max}."

    # The notice logged when the throttle feature is configured.
    NOTICE_EXPERIMENTAL = ("Throttling messages is an experimental option. It has limited support "
                           "and may cause one to miss important messages.")

    # The config parse/validate errors, raised as ValueError.
    ERROR_DUPLICATE_MESSAGE = "{message_id} has been configured multiple times"
    ERROR_INVALID_CATEGORY = "{category} is not valid. Valid categories are {valid_categories}"
    ERROR_CATEGORY_MISSING_MAX = "{category} is missing 'max' configuration option."
    ERROR_CATEGORY_MISSING_DURATION = "{category} is missing 'duration' configuration option."
    ERROR_MESSAGE_MISSING_MAX = "{message} is missing 'max' configuration option."
    ERROR_MESSAGE_MISSING_DURATION = "{message} is missing 'duration' configuration option."

    @staticmethod
    def parse_config(config):
        """ Parse the 'throttle' section of the config into the internal representation. """
        throttle_config = {'category': {}, 'message': {}}

        if 'throttle' in config:
            throttle_config['category'] = MessageThrottle._parse_categories(config['throttle'])
            throttle_config['message'] = MessageThrottle._parse_messages(config['throttle'])

        return throttle_config

    @staticmethod
    def _parse_categories(throttle):
        """ Parse the 'category' section of the throttle config. """
        categories = {}
        for category in throttle.get('category', configobj.ConfigObj({})).sections:
            if category not in MessageThrottle.VALID_CATEGORIES:
                raise ValueError(MessageThrottle.ERROR_INVALID_CATEGORY.format(
                    category=category, valid_categories=MessageThrottle.VALID_CATEGORIES))
            if 'max' not in throttle['category'][category]:
                raise ValueError(MessageThrottle.ERROR_CATEGORY_MISSING_MAX.format(category=category))
            if 'duration' not in throttle['category'][category]:
                raise ValueError(MessageThrottle.ERROR_CATEGORY_MISSING_DURATION.format(category=category))
            throttle['category'][category]['max'] = _to_int(throttle['category'][category]['max'])
            throttle['category'][category]['duration'] = _to_int(throttle['category'][category]['duration'])
            categories[category] = throttle['category'][category]

        return categories

    @staticmethod
    def _parse_messages(throttle):
        """ Parse the 'messages' section of the throttle config. """
        messages = {}
        for message in throttle.get('messages', configobj.ConfigObj({})).sections:
            MessageThrottle._validate_message(throttle['messages'][message], message)

            if 'messages' in throttle['messages'][message]:
                message_ids = _as_list(throttle['messages'][message]['messages'])
            else:
                message_ids = [message]

            for message_id in message_ids:
                message_id_int = _to_int(message_id)
                if message_id_int in messages:
                    raise ValueError(MessageThrottle.ERROR_DUPLICATE_MESSAGE.format(message_id=message_id))
                messages[message_id_int] = {
                    'duration': _to_int(throttle['messages'][message]['duration']),
                    'max': _to_int(throttle['messages'][message]['max'])
                }

        return messages

    @staticmethod
    def _validate_message(message_config, message):
        """ Validate a 'messages' section of the throttle config. """
        if 'max' not in message_config:
            raise ValueError(MessageThrottle.ERROR_MESSAGE_MISSING_MAX.format(message=message))
        if 'duration' not in message_config:
            raise ValueError(MessageThrottle.ERROR_MESSAGE_MISSING_DURATION.format(message=message))

    def __init__(self, throttle_config=None, log_summary=None):
        if throttle_config is None:
            throttle_config = {'category': {}, 'message': {}}

        self.throttle_config = throttle_config
        self.log_summary = log_summary
        self.logged_ids = {}

    def is_throttled(self, log_type, key):
        """ Return True when the message must be suppressed. """
        if key is None:
            return False
        if key in self.throttle_config['message']:
            return self._check_message(key, self.throttle_config['message'][key])
        if log_type in self.throttle_config['category']:
            return self._check_message(key, self.throttle_config['category'][log_type])
        if 'ALL' in self.throttle_config['category']:
            return self._check_message(key, self.throttle_config['category']['ALL'])

        return False

    def _check_message(self, key, throttle_config):
        if throttle_config['max'] is None:
            return False

        if throttle_config['duration'] == 0:
            return self._check_message_duration_zero(key, throttle_config)

        return self._check_message_window(key, throttle_config)

    def _check_message_duration_zero(self, key, throttle_config):
        if key not in self.logged_ids:
            self.logged_ids[key] = {}
            self.logged_ids[key]['count'] = 0

        if self.logged_ids[key]['count'] > throttle_config['max']:
            if self.logged_ids[key]['count'] % throttle_config['max'] == 0:
                self.logged_ids[key]['count'] += 1
                self._log_summary(MessageThrottle.SUMMARY_DURATION_ZERO.format(
                    count=self.logged_ids[key]['count'], max=throttle_config['max']))
                return False

        self.logged_ids[key]['count'] += 1
        return True

    def _check_message_window(self, key, throttle_config):
        now = int(time.time())
        window = int(now // throttle_config['duration'])

        if key not in self.logged_ids:
            self.logged_ids[key] = {}
            self.logged_ids[key]['window'] = window
            self.logged_ids[key]['count'] = 1
            return False

        if window != self.logged_ids[key]['window']:
            self.logged_ids[key]['count'] = 0
            self.logged_ids[key]['window'] = window

        self.logged_ids[key]['count'] += 1

        if self.logged_ids[key]['count'] > throttle_config['max']:
            if self.logged_ids[key]['count'] % throttle_config['max'] == 0:
                self._log_summary(MessageThrottle.SUMMARY_WINDOW.format(
                    count=self.logged_ids[key]['count'] - throttle_config['max'], window=window))
                return False
            return True

        return False

    def _log_summary(self, msg_text):
        """ Pass a suppression summary to the callback when one was provided. """
        if self.log_summary is not None:
            self.log_summary(msg_text)


def has_v2_api():
    """ Determine if paho mqtt's v2 callback api is available. """
    return hasattr(mqtt, 'CallbackAPIVersion')


def select_api(protocol):
    """ Select the client api variant to use for a protocol. """
    if not has_v2_api():
        return API_V1

    if protocol in MQTT3_PROTOCOLS:
        return API_V2_MQTT3

    return API_V2_MQTT5


def parse_protocol(protocol_string):
    """ Resolve a protocol name to the paho mqtt constant, 0 when unknown. """
    return getattr(mqtt, protocol_string, 0)


def create_client(api, *, client_id, protocol, userdata=None, clean_session=None):
    """ Create a paho mqtt client for the selected api variant. """
    if api == API_V1:
        return mqtt.Client(protocol=protocol,
                           client_id=client_id,
                           userdata=userdata,
                           clean_session=clean_session)

    if api not in (API_V2_MQTT3, API_V2_MQTT5):
        raise ValueError(f"Invalid api, {api}.")

    kwargs = {
        'callback_api_version': mqtt.CallbackAPIVersion.VERSION2,
        'protocol': protocol,
        'client_id': client_id,
        'userdata': userdata
    }
    if protocol != mqtt.MQTTv5:
        kwargs['clean_session'] = clean_session

    return mqtt.Client(**kwargs)


def connect(client, api, *, host, port, keepalive, clean_start=None):  # pylint: disable=too-many-arguments
    """ Connect to the broker. clean_start is only used by the v2-mqtt5 api variant. """
    if api == API_V2_MQTT5:
        client.connect(host=host, port=port, keepalive=keepalive, clean_start=clean_start)
        return

    if api not in (API_V1, API_V2_MQTT3):
        raise ValueError(f"Invalid api, {api}.")

    client.connect(host, port, keepalive)


def configure_reconnect_delay(client, *, min_delay, max_delay):
    """ Configure the paho reconnect backoff delays.

        The delays are the same for all api variants, so no api variant is needed.
    """
    client.reconnect_delay_set(min_delay=min_delay, max_delay=max_delay)


def adapt_callback(api, event, callback):
    """ Adapt a canonical callback to the calling convention of an api variant.

        The paho mqtt api variants call some callbacks with different signatures.
        A canonical callback is written with the signature of the v2 api variants,
        with 'rc' normalized to an int, 'codes' to a list of ints, and 'properties'
        to None when the api variant does not supply it:

            on_connect(client, userdata, flags, rc, properties)
            on_disconnect(client, userdata, rc, properties)
            on_subscribe(client, userdata, mid, codes, properties)
            on_publish(client, userdata, mid, properties)
    """
    try:
        v1_adapter, v2_adapter = _ADAPTERS[event]
    except KeyError:
        raise ValueError(f"Invalid event, {event}.") from None

    if api == API_V1:
        return v1_adapter(callback)

    if api in (API_V2_MQTT3, API_V2_MQTT5):
        return v2_adapter(callback)

    raise ValueError(f"Invalid api, {api}.")


def apply_credentials(client, username, password):
    """ Set the client credentials when both are configured. """
    if username is not None and password is not None:
        client.username_pw_set(username, password)


def configure_tls(client, tls_dict, *, format_error):
    """ Configure the client's TLS. """
    cert_reqs = {
        'none': ssl.CERT_NONE,
        'optional': ssl.CERT_OPTIONAL,
        'required': ssl.CERT_REQUIRED
    }.get(tls_dict.get('certs_required', 'required'))
    if cert_reqs is None:
        raise ValueError(format_error('certs_required', tls_dict['certs_required']))

    tls_version = _available_tls_versions().get(tls_dict.get('tls_version', 'tlsv12'))
    if tls_version is None:
        raise ValueError(format_error('tls_version', tls_dict['tls_version']))

    client.tls_set(ca_certs=_empty_as_unset(tls_dict.get('ca_certs')),
                   certfile=_none_as_unset(tls_dict.get('certfile')),
                   keyfile=_none_as_unset(tls_dict.get('keyfile')),
                   cert_reqs=cert_reqs,
                   tls_version=tls_version,
                   ciphers=_none_as_unset(tls_dict.get('ciphers')))


def _adapt_on_connect_v1(callback):
    def adapted(client, userdata, flags, rc):
        callback(client, userdata, flags, int(rc), None)
    return adapted

def _adapt_on_connect_v2(callback):
    def adapted(client, userdata, flags, reason_code, properties):
        callback(client, userdata, flags, int(reason_code.value), properties)
    return adapted

def _adapt_on_disconnect_v1(callback):
    def adapted(client, userdata, rc):
        callback(client, userdata, int(rc), None)
    return adapted

def _adapt_on_disconnect_v2(callback):
    def adapted(client, userdata, _disconnect_flags, reason_code, properties):
        callback(client, userdata, int(reason_code.value), properties)
    return adapted

def _adapt_on_subscribe_v1(callback):
    def adapted(client, userdata, mid, codes):
        callback(client, userdata, mid, codes, None)
    return adapted

def _adapt_on_subscribe_v2(callback):
    def adapted(client, userdata, mid, reason_codes, properties):
        callback(client, userdata, mid, [int(reason_code.value) for reason_code in reason_codes], properties)
    return adapted

def _adapt_on_publish_v1(callback):
    def adapted(client, userdata, mid):
        callback(client, userdata, mid, None)
    return adapted

def _adapt_on_publish_v2(callback):
    def adapted(client, userdata, mid, _reason_code, properties):
        callback(client, userdata, mid, properties)
    return adapted

_ADAPTERS = {
    'on_connect': (_adapt_on_connect_v1, _adapt_on_connect_v2),
    'on_disconnect': (_adapt_on_disconnect_v1, _adapt_on_disconnect_v2),
    'on_subscribe': (_adapt_on_subscribe_v1, _adapt_on_subscribe_v2),
    'on_publish': (_adapt_on_publish_v1, _adapt_on_publish_v2)
}


def _available_tls_versions():
    """ Map every tls_version name this OpenSSL build actually provides. """
    valid_tls_versions = {}
    for key, constant in SSL_PROTOCOLS:
        try:
            valid_tls_versions[key] = getattr(ssl, constant)  # NOSONAR - legacy compatibility only
        except AttributeError:
            continue
    return valid_tls_versions


def _empty_as_unset(value):
    """ Treat an empty string as not configured. """
    return None if value == '' else value


def _none_as_unset(value):
    """ Treat the literal 'none', in any case, as not configured.

        ca_certs is read with _empty_as_unset, while certfile, keyfile and
        ciphers use the literal 'none', so the two normalizations are
        deliberately distinct.
    """
    if value and value.lower() == 'none':
        return None
    return value
