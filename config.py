import os
import logging

class BaseConfig(object):
    ELASTICSEARCH_URL = 'http://elasticsearch:9200'
    LEVEL = logging.INFO

class DevConfig(BaseConfig):
    pass

class StagingConfig(BaseConfig):
    pass

class ProdConfig(BaseConfig):
    pass

env = os.getenv('STOOD_ENV')
if env == 'dev':
    config = DevConfig()
elif env == 'staging':
    config = StagingConfig()
elif env == 'prod':
    config = ProdConfig()
else:
    config = DevConfig()
