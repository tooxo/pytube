# -*- coding: utf-8 -*-

"""Various helper functions implemented by pytube."""
import functools
import logging
import os
import re
import warnings
from typing import TypeVar, Callable, Optional, Dict, List, Any

from pytube.exceptions import RegexMatchError

logger = logging.getLogger(__name__)


def regex_search(pattern: str, string: str, group: int) -> str:
    """Shortcut method to search a string for a given pattern.

    :param str pattern:
        A regular expression pattern.
    :param str string:
        A target string to search.
    :param int group:
        Index of group to return.
    :rtype:
        str or tuple
    :returns:
        Substring pattern matches.
    """
    regex = re.compile(pattern)
    results = regex.search(string)
    if not results:
        raise RegexMatchError(caller="regex_search", pattern=pattern)

    logger.debug("matched regex search: %s", pattern)

    return results.group(group)

def setup_logger(level: int = logging.ERROR):
    """Create a configured instance of logger.

    :param int level:
        Describe the severity level of the logs to handle.
    """
    fmt = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    date_fmt = "%H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=date_fmt)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # https://github.com/nficano/pytube/issues/163
    logger = logging.getLogger("pytube")
    logger.addHandler(handler)
    logger.setLevel(level)


GenericType = TypeVar("GenericType")


def cache(func: Callable[..., GenericType]) -> GenericType:
    """ mypy compatible annotation wrapper for lru_cache"""
    return functools.lru_cache()(func)  # type: ignore


def deprecated(reason: str) -> Callable:
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    def decorator(func1):
        message = "Call to deprecated function {name} ({reason})."

        @functools.wraps(func1)
        def new_func1(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                message.format(name=func1.__name__, reason=reason),
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)
            return func1(*args, **kwargs)

        return new_func1

    return decorator


def uniqueify(duped_list: List) -> List:
    seen: Dict[Any, bool] = {}
    result = []
    for item in duped_list:
        if item in seen:
            continue
        seen[item] = True
        result.append(item)
    return result
