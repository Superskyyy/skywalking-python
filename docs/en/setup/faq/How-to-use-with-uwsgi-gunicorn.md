# How to use with uWSGI/Gunicorn? (aka. pre-forking servers)
[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) 
and [Gunicorn](https://gunicorn.org/#quickstart) are two dominant pre-forking web servers in the Python ecosystem.

**Note**: After the v1.0.0 release, we have enhanced the sw-python CLI so that it will automatically handle many of the 
pre-forking server behavior in Gunicorn and uWSGI. 

Since pre-forking servers spawn multiple server processes, we consider each of the processes (workers) a new `service instance`, we
take your configuration `SW_AGENT_INSTANCE` and append it's pid to generate a unique worker instance name. In this way we will see multiple 
instances (server workers) under the same service in the SkyWalking UI dashboard. In fact, we do append `os.getpid()` for every Python agent
instance since fork is frequently used in the Python ecosystem.

You no longer need to manually specify @postfork and post_fork hooks other than running `sw-python run uwsgi/gunicorn args`. 

Still, you do need to add the post_fork hooks if you are using the legacy setup by importing skywalking in your application code. 

We encourage you to try the `sw-python` non-intrusive CLI and you can always fall back to legacy setup if unhandled cases were encountered.

<details>
  <summary>What is pre-fork</summary>
    [Pre-forking basically means a master creates forks which handle each request](https://stackoverflow.com/questions/25834333/what-exactly-is-a-pre-fork-web-server-model)
</details>

When they are used with SkyWalking, things can be complicated since `os.fork()` can lead to confusing behavior, luckily we have easy solutions listed below for your reference.

Some previous bug reports can be found here:
* [[Python] Apache Skywalking, flask uwsgi, no metrics send to server · Issue #6324 · apache/skywalking](https://github.com/apache/skywalking/issues/6324)
* [[Bug] skywalking-python not work with uwsgi + flask in master workers mode and threads mode · Issue #8566 · apache/skywalking](https://github.com/apache/skywalking/issues/8566)

# uWSGI (legacy setup)
Use the following method to call [`@postfork`](https://uwsgi-docs.readthedocs.io/en/latest/PythonDecorators.html#uwsgidecorators.postfork), the low-level API of uWSGI to initialize the SkyWalking client.

The following is an example of the use of uWSGI and Flask, the initialization parameters of SkyWalking can be referred to [Legacy Setup](https://skywalking.apache.org/docs/skywalking-python/next/en/setup/intrusive/#legacy-setup)

Note: you should not put initialization code outsided of the postfork decorator, otherwise it may trigger problems as 
threads cannot be safely forked.
```python
# main.py
from uwsgidecorators import postfork
from skywalking import agent, config

@postfork
def init_tracing():
    config.init(collector_address='127.0.0.1:11800', service_name='your awesome service')

    agent.start()

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
```

```shell
uwsgi --die-on-term \
    --http 0.0.0.0:5000 \
    --http-manage-expect \
    --master --workers 3 \
    --enable-threads \
    --threads 3 \
    --manage-script-name \
    --mount /=main:app
```

# Gunicorn (legacy setup)
Create or add the following lines to your Gunicorn [configuration file](https://docs.gunicorn.org/en/stable/configure.html) 

(Python-based, defaults to `gunicorn.conf.py`)

```Python
def post_fork(server, worker):
    from skywalking import agent, config
    config.init(collector_address='127.0.0.1:11800', service_name='your awesome service')
    agent.start()
```

```shell
gunicorn <your-args> --config file_with_above_code.py
```