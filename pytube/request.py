# -*- coding: utf-8 -*-

"""Implements a simple wrapper around aiohttp."""
import logging
from functools import lru_cache
from typing import Iterable, Dict, Optional
import aiohttp

logger = logging.getLogger(__name__)


base_headers = {"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"}


async def get(url) -> str:
    """Send an http GET request.

    :param str url:
        The URL to perform the GET request for.
    :rtype: str
    :returns:
        UTF-8 encoded string of response
    """
    async with aiohttp.request("GET", url, headers=base_headers) as res:
        return (await res.read()).decode("utf-8")


async def stream(
    url: str, chunk_size: int = 4096, range_size: int = 9437184
) -> Iterable[bytes]:
    """Read the response in chunks.
    :param str url: The URL to perform the GET request for.
    :param int chunk_size: The size in bytes of each chunk. Defaults to 4KB
    :param int range_size: The size in bytes of each range request. Defaults to 9MB
    :rtype: Iterable[bytes]
    """
    file_size: int = range_size  # fake filesize to start
    downloaded = 0
    while downloaded < file_size:
        stop_pos = min(downloaded + range_size, file_size) - 1
        range_header = f"bytes={downloaded}-{stop_pos}"
        headers = {**base_headers, "Range": range_header}
        async with aiohttp.request(
            method="GET", url=url, headers=headers
        ) as res:
            if file_size == range_size:
                try:
                    content_range = res.headers["Content-Range"]
                    file_size = int(content_range.split("/")[1])
                except (KeyError, IndexError, ValueError) as e:
                    logger.error(e)
            while True:
                chunk = await res.content.read(chunk_size)
                if not chunk:
                    break
                downloaded += len(chunk)
                yield chunk
    return  # pylint: disable=R1711


@lru_cache(maxsize=None)
async def filesize(url: str) -> int:
    """Fetch size in bytes of file at given URL

    :param str url: The URL to get the size of
    :returns: int: size in bytes of remote file
    """
    return int((await head(url))["content-length"])


async def head(url: str) -> Dict:
    """Fetch headers returned http GET request.

    :param str url:
        The URL to perform the GET request for.
    :rtype: dict
    :returns:
        dictionary of lowercase headers
    """
    async with aiohttp.request("HEAD", url) as res:
        response_headers = res.headers
        return {k.lower(): v for k, v in response_headers.items()}
