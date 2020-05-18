import logging, logging.config, requests, json
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from redlock import Redlock
from flask import current_app


s = requests.Session()
retries = Retry(total=30, backoff_factor=10)
s.mount("http://", HTTPAdapter(max_retries=retries))


def configure_logger(name, log_path):
    logging.config.dictConfig({
        "version": 1,
        "formatters": {
            "default": {"format": "%(asctime)s %(levelname)s: %(message)s  [in %(pathname)s:%(lineno)d]"}
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "formatter": "default",
                "filename": log_path,
            }
        },
        "loggers": {
            "default": {
                "level": "DEBUG",
                "handlers": ["console", "file"]
            }
        },
        "disable_existing_loggers": False
    })
    return logging.getLogger(name)


logger_app = configure_logger("default", "log_main.log")


class NLReceiver:
    def __init__(self, nl_rest_url, data_key, user="not user"):
        self.user = user
        self._dlm = Redlock([{"host": "redis_trade", "port": 6379, "db": 0}, ])
        self.error = None
        self.nl_rest_url = nl_rest_url
        self.data_key = data_key
        self.token = self._get_token
        self.data = self._get_data

    def _pause(self):

        while True:
            my_lock = self._dlm.lock("pause_for_API", 200)
            if my_lock:
                break
            print("PAUSE_FOR_API", self.user)

    def _connector(self, nl_rest_url, data_key, params):
        data_response = None
        data_result = {}
        data_result_error = None
        count = 0

        def _msg_to_logger(msg, data_response_status):
            return "USER: [{}] PAUSE_FOR_API - {} , data_response_status[\"code\"] - {}," \
                   "data_response_status - {},  - nl_rest_url {}, data_key - {}, params - {}"\
                   .format(self.user, msg, data_response_status["code"],
                           data_response_status, nl_rest_url, data_key, params)
        try:
            pause = False
            while count != 40:
                count += 1
                self._pause()
                r = s.get(nl_rest_url, params=params)
                data_response = json.loads(r.text[6:])  # JSON Hijacking
                data_response_status = data_response[data_key]["status"]
                if data_response_status["code"] == "200":
                    if pause:
                        logger_app.error(_msg_to_logger("PAUSE GOOD", data_response_status))
                    data_result = data_response[data_key]["data"]
                    break
                elif data_response_status["code"] == "4":
                    if pause:
                        logger_app.error(_msg_to_logger("PAUSE GOOD", data_response_status))
                    break
                pause = True
                logger_app.error(_msg_to_logger("PROBLEM", data_response_status))

                params = self._get_token
            else:
                raise Exception(str(data_response))

        except requests.exceptions.RequestException as e:
            msg = "USER: [{}] RequestException {}".format(self.user, str(e))
            data_result_error = msg
            logger_app.error(msg)

        except Exception as e:
            msg = "USER: [{}] Exception - {} - {} - data_response: {}".format(self.user, e.__class__, str(e),
                                                                              data_response)
            data_result_error = msg
            logger_app.error(msg)
        # else:
        #     # logger_dealer_nl.info("USER: [{}] {} {}".format(self.user, data_key, str(data_response_status)))
        #     if data_response_status["code"] == "200":
        #         data_response = data_response[data_key]["data"]
        finally:
            return {"data": data_result, "error": data_result_error}

    @property
    def _get_token(self):
        data_key = current_app.config["NL_AUTH"]["DATA_KEY"]
        nl_url_auth = current_app.config["NL_AUTH"]["URL"]
        params = {"username": current_app.config["NL_USERNAME"], "password": current_app.config["NL_PASSWORD"]}
        response = self._connector(nl_url_auth, data_key, params)
        data = response.get("data")
        token = data.get("token")
        if token:
            return {"oauth_token": token}
        if response.get("error"):
            self.error = response.get("error")

    @property
    def _get_data(self):
        if self.token:
            response = self._connector(self.nl_rest_url, self.data_key, self.token)
            self.error = response.get("error")
            return response.get("data")
        else:
            return {}

    def __str__(self):
        return "error: {}, nl_rest_url: {}, data_key: {}, token: {}, data: {}, user: {}" \
                .format(self.error, self.nl_rest_url, self.data_key, self.token, self.data, self.user,)


from flask import Blueprint
backend = Blueprint("backend", __name__)

from . import views
