from stood_python.logger.logger import get_logger

def test_logger():
    log = get_logger(name='test')
    log.info('hello world')
