import os

app_dir = os.path.abspath(os.path.dirname(__file__))
files_store_folder = os.path.join(app_dir, "files_store_folder")


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "secret key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.googlemail.com"
    MAIL_PORT = os.environ.get("MAIL_PORT") or 587
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") or True
    # MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL") or True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or "pass"
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or "pass"
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    MAIL_ADMIN = os.environ.get("MAIL_ADMIN") or "admim@admim.admim"

    ITEMS_PER_PAGE = 15

    PERMISSION = ["admin", "moderator", "user"]

    UPLOADED_PATH = os.path.join(app_dir, "files_store_folder")
    UPLOADED_MAX_FILES = 7 * 1024 * 1024

    PRODUCT_CATALOG_ROOT_DIRECTORY = "КАТАЛОГ"

    NL_USERNAME = os.environ["NL_USERNAME"]
    NL_PASSWORD = os.environ["NL_PASSWORD"]
    NL_AUTH = {"DATA_KEY": "tokenResponse", "URL": "http://services.netlab.ru/rest/authentication/token.json"}
    NL_CATALOG = {"DATA_KEY": "catalogsResponse", "URL": "http://services.netlab.ru/rest/catalogsZip/list.json"}
    NL_CATALOG_MAIN = "Прайс-лист"
    NL_CATEGORIES = {"DATA_KEY": "catalogResponse", "URL": "http://services.netlab.ru/rest/catalogsZip/{catalog_name}.json"}
    NL_GOODS = {"DATA_KEY": "categoryResponse",
                     "URL": "http://services.netlab.ru/rest/catalogsZip/{catalog_name}/{category_id}.json"}
    NL_GOOD = {"DATA_KEY": "goodsResponse",
                    "URL": "http://services.netlab.ru/rest/catalogsZip/{catalog_name}/{category_id}/{position_id}.json"}
    NL_GOOD_V2 = {"DATA_KEY": "goodsResponse",
                       "URL": "http://services.netlab.ru/rest/catalogsZip/goodsDescriptionByUid/{position_id}.json"}
    NL_IMG_GOOD = {"DATA_KEY": "entityListResponse",
                        "URL": "http://services.netlab.ru/rest/catalogsZip/goodsImages/{goodsId}.json"}
    NL_IMG_CATEGORY = {"DATA_KEY": "categoryResponse",
                        "URL": "http://services.netlab.ru/rest/catalogsZip/goodsImagesByCategory/{categoryId}.json"}
    NL_GOOD_UPDATE = {"DATA_KEY": "goodsResponse",
                       "URL": "http://services.netlab.ru/rest/catalogsZip/goodsByUid/{position_id}.json"}


POSTGRESQL = "postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(
                os.environ.get("DB_USER"),
                os.environ.get("DB_PASSWORD"),
                os.environ.get("DB_HOST"),
                os.environ.get("DB_PORT"),
                os.environ.get("DB_NAME"),
            )


class DevelopementConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEVELOPMENT_DATABASE_URI") or POSTGRESQL


class TestingConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TESTING_DATABASE_URI") or POSTGRESQL


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("PRODUCTION_DATABASE_URI") or POSTGRESQL
