# -*- coding: utf-8 -*-

"""Module to download a complete playlist from a youtube channel."""
import json
import logging
import re
from datetime import date, datetime
from typing import List, Optional, Union, Tuple, AsyncGenerator
from urllib.parse import parse_qs
from collections.abc import Sequence

from pytube import request, YouTube
from pytube.helpers import cache, deprecated, uniqueify

logger = logging.getLogger(__name__)


class Playlist(Sequence):
    """Load a YouTube playlist with URL or ID"""

    def __init__(self, html: str, playlist_id: str, playlist_url: str):

        self.html = html
        self.playlist_id = playlist_id
        self.playlist_url = playlist_url

        # Needs testing with non-English
        self.last_update: Optional[date] = None
        date_match = re.search(
            r"<li>Last updated on (\w{3}) (\d{1,2}), (\d{4})</li>", self.html
        )
        if date_match:
            month, day, year = date_match.groups()
            self.last_update = datetime.strptime(
                f"{month} {day:0>2} {year}", "%b %d %Y"
            ).date()

        self._video_regex = re.compile(r"href=\"(/watch\?v=[\w-]*)")
        self._video_regex_2 = re.compile(r"<a[A-z0-9 \"-=]+href=\"(/watch\?v="
                                         r"[A-z0-9-_]{11})[A-z0-9 \"\-&_;=]+>"
                                         r"[\s]+([^<\n]+)[\s]+(</a>)?")
        self._video_urls = []

    @classmethod
    async def create(cls, url: str):
        """
        create
        """
        try:
            playlist_id: str = parse_qs(url.split("?")[1])["list"][0]
        except IndexError:  # assume that url is just the id
            playlist_id = url

        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        html = await request.get(playlist_url)
        self = cls(html, playlist_id, playlist_url)
        await self._fill_video_urls()
        return self

    @staticmethod
    def _find_load_more_url(req: str) -> Optional[str]:
        """Given an html page or fragment, returns the "load more" url if found."""
        match = re.search(
            r"data-uix-load-more-href=\"(/browse_ajax\?"
            'action_continuation=.*?)"',
            req,
        )
        if match:
            return f"https://www.youtube.com{match.group(1)}"

        return None

    async def _paginate(
        self
    ) -> AsyncGenerator[List[Tuple[str, str]], None]:
        """Parse the video links from the page source, yields the /watch?v= part from video link
        """
        req = self.html
        videos_urls = self._extract_videos(req)
        yield videos_urls

        # The above only returns 100 or fewer links
        # Simulating a browser request for the load more link
        load_more_url = self._find_load_more_url(req)

        while load_more_url:  # there is an url found
            logger.debug("load more url: %s", load_more_url)
            req = await request.get(load_more_url)
            load_more = json.loads(req)
            try:
                html = load_more["content_html"]
            except KeyError:
                logger.debug("Could not find content_html")
                return
            videos_urls = self._extract_videos(html)
            yield videos_urls

            load_more_url = self._find_load_more_url(
                load_more["load_more_widget_html"]
            )

        return

    def _extract_videos(self, html: str) -> List[Tuple[str, str]]:
        matches = self._video_regex_2.findall(html)
        _list: List[Tuple[str, str]] = []
        for match in matches:
            _list.append((self._video_url(match[0]), match[1]))
        return uniqueify(_list)

    async def _fill_video_urls(self) -> None:
        """Complete links of all the videos in playlist

        :rtype: List[str]
        :returns: List of video URLs
        """
        async for page in self._paginate():
            for video in page:
                self._video_urls.append(
                    video
                )

    @property
    def video_urls(self) -> List[Tuple[str, str]]:
        """Return all video urls
        """
        return self._video_urls

    def __getitem__(self, i: Union[slice, int]) -> Union[Tuple[str, str], List[Tuple[str, str]]]:
        return self.video_urls[i]

    def __len__(self) -> int:
        return len(self.video_urls)

    def __repr__(self) -> str:
        return f"{self.video_urls}"

    @deprecated("This function will be removed in the future.")
    def _path_num_prefix_generator(self, reverse=False):  # pragma: no cover
        """Generate number prefixes for the items in the playlist.

        If the number of digits required to name a file,is less than is
        required to name the last file,it prepends 0s.
        So if you have a playlist of 100 videos it will number them like:
        001, 002, 003 ect, up to 100.
        It also adds a space after the number.
        :return: prefix string generator : generator
        """
        digits = len(str(len(self.video_urls)))
        if reverse:
            start, stop, step = (len(self.video_urls), 0, -1)
        else:
            start, stop, step = (1, len(self.video_urls) + 1, 1)
        return (str(i).zfill(digits) for i in range(start, stop, step))

    @cache
    def title(self) -> Optional[str]:
        """Extract playlist title

        :return: playlist title (name)
        :rtype: Optional[str]
        """
        pattern = re.compile("<title>(.+?)</title>")
        match = pattern.search(self.html)

        if match is None:
            return None

        return match.group(1).replace("- YouTube", "").strip()

    @staticmethod
    def _video_url(watch_path: str):
        return f"https://www.youtube.com{watch_path}"
