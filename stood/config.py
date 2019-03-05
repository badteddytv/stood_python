import os
import logging

class BaseConfig(object):
    ELASTICSEARCH_URL = 'http://elasticsearch:9200'
    LEVEL = logging.INFO
    ELASTICSEARCH_ENABLED = True

class DevConfig(BaseConfig):
    ELASTICSEARCH_ENABLED = False

class StagingConfig(BaseConfig):
    pass

class ProdConfig(BaseConfig):
    pass

class LocalConfig(BaseConfig):
    ELASTICSEARCH_URL = 'http://localhost:9200'

env = os.getenv('STOOD_ENV')
if env == 'dev':
    config = DevConfig()
elif env == 'staging':
    config = StagingConfig()
elif env == 'prod':
    config = ProdConfig()
elif env == 'local':
    config = LocalConfig()
else:
    config = DevConfig()
