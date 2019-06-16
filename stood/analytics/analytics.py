import os
import sys
import uuid
import datetime
import traceback
import json
from stood.config import config
import logging
from logging import StreamHandler, Formatter
from logging.handlers import RotatingFileHandler
import time

hostname = os.getenv('HOSTNAME', 'NO_HOSTNAME')


logger = None


def get_logger(name):
    global logger

    if logger is not None:
        return logger

    logger = logging.getLogger('{}-analytics'.format(name))
    logger.setLevel(config.LEVEL)

    elasticsearch_handler = RotatingFileHandler(
            '/var/log/stood/{}.analytics'.format(name), maxBytes=1024 * 100, backupCount=10)
    logger.addHandler(elasticsearch_handler)

    return logger


class EventTracker(object):
    def __init__(self, name):
        self.name = name
        self.logger = get_logger(name)

    def track_event(self, routing_key, data):
        new_day = get_current_day()
        index = 'log-{}'.format(new_day)

        es_record = {
                '_index': index,
                '_type': '_doc',
                '_id': str(uuid.uuid4()),
                'timestamp': int(time.time() * 1000),
                'service': self.name,
                'routing_key': routing_key,
                'data': data,
                'hostname': hostname
                }

        self.logger.info(json.dumps(es_record))


def get_current_day():
    return datetime.datetime.today().strftime('%Y-%m-%d')


def get_event_tracker(name):
    return EventTracker(name)


if __name__ == '__main__':
    test_data = {'data': 'data'}
    et = get_event_tracker(name='test')
    et.track_event(routing_key='test.test', data=test_data)
    et.track_event(routing_key='test.test.another', data=test_data)
