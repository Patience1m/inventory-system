class BaseConfig:
    SEED_DATA: bool = False

class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    SEED_DATA: bool = True

class TestingConfig(BaseConfig):
    TESTING: bool = True
    SEED_DATA: bool = True

class ProductionConfig(BaseConfig):
    DEBUG: bool = False

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}