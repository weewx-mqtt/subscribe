#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

"""Test helpers shared by the MQTTSubscribe service and driver unit tests."""

import time

import mock


_MISSING = object()


def as_generator(items):
    """ Yield the items of a list as a generator. """
    for item in items:
        yield item


def empty_generator():
    """ An exhausted generator for the empty-queue cases. """
    return iter(())


def archive_window(interval=300):
    """ The start/end timestamps of the archive period just after now. """
    current_time = int(time.time() + 0.5)
    end_ts = (int(current_time / interval) + 1) * interval
    return end_ts - interval, end_ts


def create_queue(topic):
    """ The minimal queue descriptor the subscriber expects. """
    return dict({'name': topic})


def configure_mock_subscriber(mock_subscriber, *, queues=_MISSING, get_data=_MISSING,
                              get_data_side_effect=_MISSING, get_accumulated_data=_MISSING,
                              cached_fields=_MISSING, subscribed_topics=_MISSING):
    """ Configure a patched MQTTSubscriber instance's properties and data methods. """
    instance = mock_subscriber.return_value
    for name, value in (('queues', queues), ('cached_fields', cached_fields),
                        ('subscribed_topics', subscribed_topics)):
        if value is not _MISSING:
            setattr(type(instance), name, mock.PropertyMock(return_value=value))
    if get_data is not _MISSING:
        type(instance).get_data = mock.Mock(return_value=get_data)
    if get_data_side_effect is not _MISSING:
        type(instance).get_data = mock.Mock(side_effect=get_data_side_effect)
    if get_accumulated_data is not _MISSING:
        type(instance).get_accumulated_data = mock.Mock(return_value=get_accumulated_data)
