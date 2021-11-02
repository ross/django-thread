## Helpers for using Django from threads

When handling requests django [manages database connection lifecycles for
you](https://github.com/django/django/blob/ca9872905559026af82000e46cde6f7dedc897b6/django/db/__init__.py#L34-L42).  By default closing them after each request or keeping
them alive allowing re-use for a specified amount of time when `CONN_MAX_AGE` is set so long as no errors are encountered.

Sometimes you want to do work outside of a web request. When the work is large and you would like to distribute it, likely to places other than where the web requests are
served, there are systems like [Celery](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html).  There are other cases though were you're just trying
to do work outside of the request & response cycle even and it's lightweight enough that running a full-blown job queuing system and it's associated data store is too
involved.  You just want [Thread](https://docs.python.org/3/library/threading.html#thread-objects)s or even better a
[ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor).

If you just jump straight in and use either of those you'll run into slow to manifest and tough to track down problems with broken database connections.  This is because
Django automatically opens a connection per-thread when a database is accessed and leaves them lying around in that thread indefinitely.  This results in errors when the
database has timed out the connection or it has otherwise encountered problems.

`django_thread` provides a this problem by implementing a `Thread` class that mimics Django's request connection handling and provides a `ThreadPoolExecutor` that does so
around the invocations of submitted calls.

## Usage

### Thread

`django_thread.Thread` is a 100% drop-in replacement for `threading.Thread`.  See [threading.Thread](https://docs.python.org/3/library/threading.html#thread-objects) for
usage and documentation.

```python
from django_thread import Thread


class ExampleThread(Thread):
    def run(self):
        for some_model in SomeModel.objects.filter(...):
            ...


thread = ExampleThread()
thread.start()
# do other things
thread.join()
```

### ThreadPoolExecutor

`django_thread.ThreadPoolExecutor` is a 100% drop-in replacement for `concurrent.futures.ThreadPoolExecutor`.  See
[concurrent.futures.ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor) for usage and documentation.

```python
from concurrent.futures import as_completed
from django_thread import ThreadPoolExecutor


def update_or_create_thing(name):
    thing, _ = Thing.objects.update_or_create(name=name)
    return thing.id


executor = ThreadPoolExecutor()

futures = []
for i in range(5):
    future = executor.submit(update_or_create_thing, f'Name i')
    futures.append(future)

ids = [f.result() for f in futures]
```
