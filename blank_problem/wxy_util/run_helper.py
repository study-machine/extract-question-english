# coding=utf8
import time
import traceback


def run_helper(logger=None, exception_callback=None):
    """
    执行装饰器
    :param logger:              日志句柄，用于异常停止信息保存到日志
    :param exception_callback:  异常回调，用于在异常停止之前处理一些事情
    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                fn(*args, **kwargs)
            except Exception:
                if logger:
                    logger.critical(traceback.format_exc())
                else:
                    print(traceback.format_exc())
                if exception_callback:
                    exception_callback()

            end = time.time()
            if logger:
                logger.info('%s is end,during %0.2f secends.' % (fn.__name__, end - start))
            return

        return wrapper

    return decorator
