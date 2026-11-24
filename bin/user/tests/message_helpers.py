#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

"""MQTT message stub shared by the four MQTTSubscribe test suites."""


class Msg:
    """Minimal stand-in for a paho MQTTMessage."""

    # pylint: disable=too-few-public-methods
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain


def create_message(topic, payload, qos=0, retain=0):
    """Build a message stub; most tests use the qos/retain defaults."""
    return Msg(topic, payload, qos, retain)
