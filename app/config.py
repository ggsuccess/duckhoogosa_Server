class Base(object):
    APP_NAME = 'Duck_API_Server'
    TESTING = True
    DEBUG = True
    DATABASE_NAME = 'NONE'


class DevelopmentConfig(Base):
    DEBUG = True
    TESTING = True
    PORT = 8000
    SERVER_HOST = '127.0.0.1'
    DATABASE_NAME = 'duckdevdb'
    CLIENT_HOST = 'http://localhost:3000'


class TestConfig(Base):
    DEBUG = True
    TESTING = True
    PORT = 7999
    SERVER_HOST = '172.31.32.164'
    DATABASE_NAME = 'ducktestdb'
    CLIENT_HOST = 'http://duckhoo.site'


class ProductionConfig(Base):
    DEBUG = True
    PORT = 8000
    SERVER_HOST = '172.31.32.164'
    DATABASE_NAME = 'duckproductiondb'
    CLIENT_HOST = 'http://duckhoo.site'
