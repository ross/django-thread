from concurrent.futures import as_completed
from django.core.management.base import BaseCommand
from logging import getLogger
from random import uniform
from time import sleep

from simple.models import Item

from django_thread import Thread, ThreadPoolExecutor


class ManageItemThread(Thread):
    log = getLogger('ManageItemThread')

    def __init__(self, key, value, min_sleep=1, max_sleep=5):
        super().__init__(name=f'manage-item-thread-{key}')
        self.key = key
        self.value = value
        self.sleep = uniform(min_sleep, max_sleep)
        self.log.info(
            '__init__: key=%s, value=%s, sleep=%f', key, value, self.sleep
        )

    def run(self):
        sleep(self.sleep)
        item, created = Item.objects.update_or_create(
            key=self.key, defaults={'value': self.value}
        )
        if created:
            self.log.info(
                'run: created "%s"="%s", id=%d', item.key, item.value, item.id
            )
        else:
            self.log.info(
                'run: updated "%s"="%s", id=%d', item.key, item.value, item.id
            )


log = getLogger('delete_item')


def delete_item(key, min_sleep=1, max_sleep=5):
    delay = uniform(min_sleep, max_sleep)
    log.info('sleep=%f', delay)
    sleep(delay)
    try:
        item = Item.objects.get(key=key)
        item.delete()
        log.info('item "%s"="%s" deleted', item.key, item.value)
        return (key, 'deleted')
    except Item.DoesNotExist:
        log.info('item key="%s", does not exist', key)
        return (key, 'noop')


class Command(BaseCommand):
    ITEMS = {'foo': 'bar', 'baz': 'blip', 'bleep': 'boop'}

    log = getLogger('Workers')

    def threads(self):
        threads = []
        for key, value in self.ITEMS.items():
            thread = ManageItemThread(key, value)
            threads.append(thread)
            thread.start()

        self.log.info('threads: waiting')
        for thread in threads:
            thread.join()
        self.log.info('threads: done')

    def pool(self):
        max_workers = int(len(self.ITEMS) / 2 + 0.5)
        self.log.info('pool: submitting, max_workers=%d', max_workers)
        executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix='thread-pool-executor'
        )
        futures = []
        for key, value in self.ITEMS.items():
            future = executor.submit(delete_item, key)
            futures.append(future)

        self.log.info('pool: waiting')
        for future in as_completed(futures):
            key, op = future.result()
            self.log.info('pool: key=%s, op=%s', key, op)
        self.log.info('pool: done')

    def handle(self, *args, **options):
        self.threads()
        self.pool()
