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
    SERVER_HOST = 'ec2-54-180-82-249.ap-northeast-2.compute.amazonaws.com'
    DATABASE_NAME = 'ducktestdb'
    CLIENT_HOST = 'https://duckhoo.site'


class ProductionConfig(Base):
    DEBUG = True
    PORT = 8000
    SERVER_HOST = 'ec2-54-180-82-249.ap-northeast-2.compute.amazonaws.com'
    DATABASE_NAME = 'duckproductiondb'
    CLIENT_HOST = 'https://duckhoo.site'
