import os
import logging
import aiohttp
import asyncio
import queue
import sys
from logging import StreamHandler
from config import config

class Elasticsearch(object):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.setup())
        self.queue = queue.Queue()

    async def setup(self):
        self.http_client = aiohttp.ClientSession()

    async def _loop(self):
        while True:
            await self._send_logs()
            await asyncio.sleep(60)

    def add_msg(self, msg):
        self.queue.put(msg)

    async def _send_logs(self):
        for msg in self.queue:
            pass

class LoggerHandler(StreamHandler):
    def __init__(self, elasticsearch):
        super().__init__()
        self.elasticsearch = elasticsearch

    def emit(self, record):
        msg = self.format(record)
        self.elasticsearch.add_msg(msg)

logger = None

def get_logger(name):
    global logger

    if logger is not None:
        return logger

    elasticsearch = Elasticsearch()
    logger = logging.getLogger(name)
    logger.setLevel(config.LEVEL)

    es_handler = LoggerHandler(elasticsearch)

    stream_handler = StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(filename)s(%(lineno)d):%(funcName)s %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(es_handler)

    return logger

if __name__ == '__main__':
    l = get_logger(name='test')
    l.info('hello')
