import os

app_dir = os.path.abspath(os.path.dirname(__file__))
files_store_folder = os.path.join(app_dir, "files_store_folder")


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "secret key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = "redis://{}:6379/0".format(os.environ.get("REDIS_HOST"))
    RABBITMQ_URL = "amqp://{}:{}@{}:5672/{}".format(os.environ["RABBITMQ_USER"], os.environ["RABBITMQ_PASSWORD"],
                                                    os.environ["RABBITMQ_HOST"], os.environ["RABBITMQ_VHOST"])

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
    # MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL") or True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    MAIL_ADMIN = os.environ.get("MAIL_ADMIN")

    ITEMS_PER_PAGE = 150

    PERMISSION = ["admin", "moderator", "user"]

    UPLOADED_PATH = os.path.join(app_dir, "files_store_folder")
    UPLOADED_MAX_FILES = 7 * 1024 * 1024

    PRODUCT_CATALOG_ROOT_DIRECTORY = "КАТАЛОГ"

    NL_USERNAME = os.environ.get("NL_USERNAME")
    NL_PASSWORD = os.environ.get("NL_PASSWORD")
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

    LOGOTYPE = "&100123939"

    UPLOAD_FOLDER = os.path.join(app_dir, "app/static/images/")
    DEFAULT_IMAGE_FOR_CATALOG = os.path.join(app_dir, "app/static/images/default.jpg")

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
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(app_dir, "test_app.db")


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("PRODUCTION_DATABASE_URI") or POSTGRESQL
