'Helpers for using Django from threads'

from django.db import close_old_connections
from threading import Thread as BaseThread
from concurrent.futures import ThreadPoolExecutor as BaseThreadPoolExecutor

__VERSION__ = '0.0.1'


class Thread(BaseThread):
    def start(self):
        close_old_connections()
        super().start()

    # TODO: would be nice if there was a place to hook in after run exits that
    # doesn't require overriding a _ method.
    def _bootstrap_inner(self):
        super()._bootstrap_inner()
        close_old_connections()


class ThreadPoolExecutor(BaseThreadPoolExecutor):
    def submit(self, fn, *args, **kwargs):
        def wrap(*wargs, **wkwargs):
            close_old_connections()
            try:
                return fn(*wargs, **wkwargs)
            finally:
                close_old_connections()

        return super().submit(wrap, *args, **kwargs)
