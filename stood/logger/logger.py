import os
import logging
import sys
import uuid
import datetime
import traceback
from logging import StreamHandler, Formatter
from logging.handlers import RotatingFileHandler
from stood.config import config
import json

hostname = os.getenv('HOSTNAME', 'NO_HOSTNAME')


def get_current_day():
    return datetime.datetime.today().strftime('%Y-%m-%d')


class EsFormatter(Formatter):
    def __init__(self, *args):
        super().__init__(*args)

    def format(self, record):
        new_day = get_current_day()
        index = 'log-{}'.format(new_day)

        es_record = {
                '_index': index,
                '_type': '_doc',
                '_id': str(uuid.uuid4()),
                'file': record.pathname,
                'line': record.lineno,
                'msg': record.msg,
                'level': record.levelname,
                'timestamp': int(record.created * 1000),
                'service': record.name,
                'func': record.funcName,
                'hostname': hostname
                }

        if record.exc_info:
            es_record['exception'] = ''.join(traceback.format_exception(*record.exc_info))

        json_string = json.dumps(es_record)

        return json_string

    def emit(self, record):
        self.add_record(record)


logger = None


def get_logger(name):
    global logger

    if logger is not None:
        return logger

    logger = logging.getLogger(name)
    logger.setLevel(config.LEVEL)

    elasticsearch_handler = RotatingFileHandler(
            '/var/log/stood/{}.log'.format(name), maxBytes=1024 * 100, backupCount=5)
    es_formatter = EsFormatter()
    elasticsearch_handler.setFormatter(es_formatter)
    logger.addHandler(elasticsearch_handler)

    stream_handler = StreamHandler(sys.stdout)
    formatter = logging.Formatter(
            '%(filename)s(%(lineno)d):%(funcName)s %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger


if __name__ == '__main__':
    log = get_logger(name='test')
    log.info('hello')
    log.info('world')
    log.error('uh oh')

    try:
        raise Exception('test exception')
    except Exception:
        log.exception('exception thrown')
