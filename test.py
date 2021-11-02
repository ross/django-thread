from unittest import TestCase
from mock import patch

from django_thread import Thread, ThreadPoolExecutor


class TestThreads(TestCase):
    @patch('django_thread.close_old_connections')
    def test_thread(self, close_old_connections_mock):

        tc = self

        class TestThread(Thread):
            def __init__(self):
                super().__init__()
                self.has_run = False

            def run(self):
                tc.assertEqual(
                    1,
                    close_old_connections_mock.call_count,
                    'has been called once before',
                )
                self.has_run = True

        close_old_connections_mock.reset_mock()
        thread = TestThread()
        self.assertFalse(thread.has_run)
        thread.start()
        self.assertTrue(thread.has_run)
        self.assertEqual(
            2, close_old_connections_mock.call_count, 'was called again after'
        )
        thread.join()

    @patch('django_thread.close_old_connections')
    def test_thread_pool_executor(self, close_old_connections_mock):
        def pretend_work(value):
            # was called before function
            close_old_connections_mock.assert_called()
            return value

        executor = ThreadPoolExecutor()

        # start out with a single submit so that we can validate when things
        # happen, not just that they did some number of times
        future = executor.submit(pretend_work, 42)
        # block and wait for completion
        self.assertEqual(
            42, future.result(), 'correct return value passed through'
        )
        self.assertEqual(
            2, close_old_connections_mock.call_count, 'was called again after'
        )

        close_old_connections_mock.reset_mock()

        # now make sure it was called for every submit
        futures = []
        for i in range(5):
            future = executor.submit(pretend_work, i)
            futures.append(future)
        # correct return values
        self.assertEqual([0, 1, 2, 3, 4], sorted([f.result() for f in futures]))
        self.assertEqual(
            10,
            close_old_connections_mock.call_count,
            'was called 10 times for 5 submits',
        )
