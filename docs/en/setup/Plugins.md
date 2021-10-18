# Supported Libraries
The following table is automatically generated from SkyWalking Python testing matrix.

The column `Versions` only indicates that library versions tested in the best effort manner.

If you find newer major versions that are missing from the following table, 
please PR to update the test matrix in each plugin.

Library | Versions | Plugin Name
| :--- | :--- | :--- |
| [aiohttp](https://docs.aiohttp.org/en/stable/) | >= 3.7.3 | `sw_aiohttp` |
| [celery](https://docs.celeryproject.org/) | >= 4.2.1 | `sw_celery` |
| [Django](https://www.djangoproject.com/) | >=2.0 <= 3.1 | `sw_django` |
| [elasticsearch](https://github.com/elastic/elasticsearch-py) | 7.9.0 | `sw_elasticsearch` |
| [falcon-hug](https://falcon.readthedocs.io/en/stable/) | >= 1.4.1 | `sw_falcon` |
| [Flask](https://flask.palletsprojects.com/en) | >=1.0.4 <= 1.1.2 | `sw_flask` |
| [http.server](https://docs.python.org/3/library/http.server.html) | Python 3.6 ~ 3.10 | `sw_http_server` |
| [kafka-python](https://kafka-python.readthedocs.io/en/master/) | 2.0.1 | `sw_kafka` |
| [psycopg2](https://www.psycopg.org/) | >= 2.8.6 | `sw_psycopg2` |
| [pymongo](https://pymongo.readthedocs.io/en/stable/) | 3.11.0 | `sw_pymongo` |
| [PyMySQL](https://pymysql.readthedocs.io/en/latest/) | 0.10.0 | `sw_pymysql` |
| [pyramid](https://trypyramid.com) | >= 1.9 | `sw_pyramid` |
| [pika](https://pika.readthedocs.io/en/stable/) | 1.1.0 | `sw_rabbitmq` |
| [redis-py](https://github.com/andymccurdy/redis-py/) | 3.5.3 | `sw_redis` |
| [requests](https://requests.readthedocs.io/en/master/) | >= 2.9.0 < 2.15.0, >= 2.17.0 <= 2.24.0 | `sw_requests` |
| [sanic](https://sanic.readthedocs.io/en/latest/) | >= 20.3.0 < 21.0.0 | `sw_sanic` |
| [tornado](https://www.tornadoweb.org/en/stable/) | >=5.0 | `sw_tornado` |
| [urllib3](https://urllib3.readthedocs.io/en/latest/) | >= 1.25.9 <= 1.25.10 | `sw_urllib3` |
| [urllib.request](https://docs.python.org/3/library/urllib.request.html) | Python 3.6 ~ 3.10 | `sw_urllib_request` |

* Note: The celery server running with "celery -A ..." should be run with the HTTP protocol as it uses multiprocessing by default which is not compatible with the gRPC protocol implementation in SkyWalking currently. Celery clients can use whatever protocol they want.

