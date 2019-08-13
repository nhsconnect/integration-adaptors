import asyncio


def async_test(f):
    """
    A wrapper for asynchronous tests.
    By default unittest will not wait for asynchronous tests to complete even if the async functions are awaited.
    By annotating a test method with `@async_test` it will cause the test to wait for asynchronous activities
    to complete
    :param f:
    :return:
    """
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        asyncio.run(future)

    return wrapper


def awaitable(result):
    """
    Create a :class:`asyncio.Future` that is completed and returns result.

    :param result: to return
    :return: a completed :class:`asyncio.Future`
    """
    future = asyncio.Future()
    future.set_result(result)
    return future
