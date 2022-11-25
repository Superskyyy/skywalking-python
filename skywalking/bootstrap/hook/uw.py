"""
Post-fork hook for uWSGI

We simply inject this module for users, so they don't need to provide a @postfork hook

Used by: bootstrap/cli/sw_python.py to inject uWSGI option --import [this module]

Potential issue, if the user also uses --import, what would happen?


This is a workaround for the fact that uwsgi has problems with forking signal as of
2022, https://github.com/unbit/uwsgi/pull/2388 - fixed but lock exception occurs
https://github.com/unbit/uwsgi/issues/1978 - not fixed

For Gunicorn - we don't use a hook, since it's not possible to inject a hook without overriding
the entire gunicorn config file, which is not a good idea. Instead, inside the sitecustomize.py we
inject a gunicorn hook that will start the agent after the worker is forked. (with os.register_at_fork)
"""
from uwsgidecorators import postfork
import os
from skywalking import agent, config

config.init(collector_address='localhost:12800', protocol='http', service_name='test-fastapi-service',
            log_reporter_active=True, service_instance=f'test_instance-{os.getpid()} forkfork',
            logging_level='CRITICAL')


@postfork
def setup_agent():
    print('postfork uwsgi called')
    agent.start()
