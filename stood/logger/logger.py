import os
import logging
import queue
import sys
import time
import uuid
import datetime
import traceback
from threading import Thread
from logging import StreamHandler
from stood.config import config
from elasticsearch import Elasticsearch
import elasticsearch.helpers as helpers

  #"doc_type": "logs-*",
MAPPINGS = """
{
  "mappings": {
    "_doc": {
      "properties": {
        "timestamp": {
          "type": "date"
        }
      }
    }
  }
}
"""

class ElasticsearchHandler(StreamHandler):
    def __init__(self):
        super().__init__()
        self.es = None
        self.queue = queue.Queue()
        loop_thread = Thread(target=self._loop)
        loop_thread.start()

        setup_thread = Thread(target=self.setup)
        setup_thread.start()

    def setup(self):
        try:
            self.es = Elasticsearch(
                    [config.ELASTICSEARCH_URL],
                    sniff_on_start=True,
                    sniff_on_connectoin_fail=True,
                    snifffer_timeout=30
                    )
            current_day = datetime.datetime.today().strftime('%Y-%m-%d')
            res = self.es.indices.create('log-{}'.format(current_day), ignore=400, body=MAPPINGS)

        except Exception:
            traceback.print_exc()
            time.sleep(15)
            self.setup()

    def _loop(self):
        while True:
            time.sleep(10)
            self._send_logs()

    def add_record(self, record):
        self.queue.put(record)

    def _send_logs(self):
        current_day = datetime.datetime.today().strftime('%Y-%m-%d')
        index = 'log-{}'.format(current_day)
        payload = []
        try:
            record = self.queue.get_nowait()
        except queue.Empty:
            record = None
        while record is not None:
            payload.append({
                '_index': index,
                '_type': '_doc',
                '_id': uuid.uuid4(),
                'file': record.pathname,
                'line': record.lineno,
                'msg': record.message,
                'level': record.levelname,
                'timestamp': int(record.created * 1000),
                'service': record.name
                })
            try:
                record = self.queue.get_nowait()
            except queue.Empty:
                record = None

        if self.es is None:
            print('ERROR: dropped logs')
            return

        helpers.bulk(self.es, payload)

    def emit(self, record):
        self.add_record(record)

logger = None

def get_logger(name):
    global logger

    if logger is not None:
        return logger

    logger = logging.getLogger(name)
    logger.setLevel(config.LEVEL)

    if config.ELASTICSEARCH_ENABLED:
        elasticsearch_handler = ElasticsearchHandler()
        logger.addHandler(elasticsearch_handler)

    stream_handler = StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(filename)s(%(lineno)d):%(funcName)s %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger

if __name__ == '__main__':
    l = get_logger(name='test')
    l.info('hello')
    l.info('world')
    l.error('uh oh')
