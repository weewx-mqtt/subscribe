#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
""" Common paho mqtt code for the weewx-mqtt extensions. """
import ssl

import paho.mqtt.client as mqtt

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
