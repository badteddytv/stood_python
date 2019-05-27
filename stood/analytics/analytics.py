import os
import queue
import sys
import time
import uuid
import datetime
import traceback
from threading import Thread
from stood.config import config
from elasticsearch import Elasticsearch
import elasticsearch.helpers as helpers

hostname = os.getenv('HOSTNAME', 'NO_HOSTNAME')

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


class DummyEventTracker(object):
    def track_event(self, routing_key, data):
        pass


def get_current_day():
    return datetime.datetime.today().strftime('%Y-%m-%d')


class EventTracker(object):
    def __init__(self, name):
        self.es = None
        self.name = name
        self.queue = queue.Queue()
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
            loop_thread = Thread(target=self._loop)
            loop_thread.start()
        except Exception:
            traceback.print_exc()
            time.sleep(15)
            self.setup()

    def _loop(self):
        while True:
            time.sleep(10)
            self._send_events()

    def track_event(self, routing_key, data):
        self.queue.put((routing_key, data))

    def _send_events(self):

        try:
            new_day = get_current_day()
            index = 'analytics-{}'.format(new_day)

            if not self.es.indices.exists(index=index):
                self.es.indices.create(index, ignore=400, body=MAPPINGS)

            current_time = datetime.datetime.now().timestamp()
        except Exception:
            traceback.print_exc()
            return

        payload = []

        try:
            routing_key, data = self.queue.get_nowait()
        except queue.Empty:
            routing_key = None
            data = None
        while routing_key is not None:
            payload.append({
                '_index': index,
                '_type': '_doc',
                '_id': uuid.uuid4(),
                'timestamp': int(current_time * 1000),
                'service': self.name,
                'routing_key': routing_key,
                'data': data,
                'hostname': hostname
                })
            try:
                routing_key = self.queue.get_nowait()
            except queue.Empty:
                routing_key = None

        if self.es is None:
            print('ERROR: dropped logs')
            return

        helpers.bulk(self.es, payload)


logger = None


def get_event_tracker(name):
    if config.ELASTICSEARCH_ENABLED:
        return EventTracker(name)

    return DummyEventTracker()


if __name__ == '__main__':
    test_data = {'data': 'data'}
    l = get_event_tracker(name='analytics')
    l.track_event(routing_key='test.test', data=test_data)
    while True:
        pass
