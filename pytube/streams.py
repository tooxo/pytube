# -*- coding: utf-8 -*-

"""
This module contains a container for stream manifest data.

A container object for the media stream (video only / audio only / video+audio
combined). This was referred to as ``Video`` in the legacy pytube version, but
has been renamed to accommodate DASH (which serves the audio and video
separately).
"""

from datetime import datetime
import logging
import os
from typing import Dict, Tuple, Optional, BinaryIO
from urllib.parse import parse_qs

from pytube import extract
from pytube import request
from pytube.itags import get_format_profile
from pytube.monostate import Monostate

logger = logging.getLogger(__name__)


class Stream:
    """Container for stream manifest data."""

    def __init__(self, stream: Dict, player_config_args: Dict, monostate: Monostate):
        """Construct a :class:`Stream <Stream>`.

        :param dict stream:
            The unscrambled data extracted from YouTube.
        :param dict player_config_args:
            The data object containing video media data like title and
            keywords.
        :param dict monostate:
            Dictionary of data shared across all instances of
            :class:`Stream <Stream>`.
        """
        # A dictionary shared between all instances of :class:`Stream <Stream>`
        # (Borg pattern).
        self._monostate = monostate

        self.url = stream["url"]  # signed download url
        self.itag = int(stream["itag"])  # stream format id (youtube nomenclature)

        # set type and codec info

        # 'video/webm; codecs="vp8, vorbis"' -> 'video/webm', ['vp8', 'vorbis']
        self.mime_type, self.codecs = extract.mime_type_codec(stream["type"])

        # 'video/webm' -> 'video', 'webm'
        self.type, self.subtype = self.mime_type.split("/")

        # ['vp8', 'vorbis'] -> video_codec: vp8, audio_codec: vorbis. DASH
        # streams return NoneType for audio/video depending.
        self.video_codec, self.audio_codec = self.parse_codecs()

        self.is_otf: bool = stream["is_otf"]
        self.bitrate: Optional[int] = stream["bitrate"]

        self._filesize: Optional[int] = None  # filesize in bytes

        # Additional information about the stream format, such as resolution,
        # frame rate, and whether the stream is live (HLS) or 3D.
        itag_profile = get_format_profile(self.itag)
        self.is_dash = itag_profile["is_dash"]
        self.abr = itag_profile["abr"]  # average bitrate (audio streams only)
        self.fps = itag_profile["fps"]  # frames per second (video streams only)
        self.resolution = itag_profile["resolution"]  # resolution (e.g.: "480p")
        self.is_3d = itag_profile["is_3d"]
        self.is_hdr = itag_profile["is_hdr"]
        self.is_live = itag_profile["is_live"]

        # The player configuration, contains info like the video title.
        self.player_config_args = player_config_args

    @property
    def is_adaptive(self) -> bool:
        """Whether the stream is DASH.

        :rtype: bool
        """
        # if codecs has two elements (e.g.: ['vp8', 'vorbis']): 2 % 2 = 0
        # if codecs has one element (e.g.: ['vp8']) 1 % 2 = 1
        return bool(len(self.codecs) % 2)

    @property
    def is_progressive(self) -> bool:
        """Whether the stream is progressive.

        :rtype: bool
        """
        return not self.is_adaptive

    @property
    def includes_audio_track(self) -> bool:
        """Whether the stream only contains audio.

        :rtype: bool
        """
        return self.is_progressive or self.type == "audio"

    @property
    def includes_video_track(self) -> bool:
        """Whether the stream only contains video.

        :rtype: bool
        """
        return self.is_progressive or self.type == "video"

    def parse_codecs(self) -> Tuple[Optional[str], Optional[str]]:
        """Get the video/audio codecs from list of codecs.

        Parse a variable length sized list of codecs and returns a
        constant two element tuple, with the video codec as the first element
        and audio as the second. Returns None if one is not available
        (adaptive only).

        :rtype: tuple
        :returns:
            A two element tuple with audio and video codecs.

        """
        video = None
        audio = None
        if not self.is_adaptive:
            video, audio = self.codecs
        elif self.includes_video_track:
            video = self.codecs[0]
        elif self.includes_audio_track:
            audio = self.codecs[0]
        return video, audio

    @property
    async def filesize(self) -> int:
        """File size of the media stream in bytes.

        :rtype: int
        :returns:
            Filesize (in bytes) of the stream.
        """
        if self._filesize is None:
            self._filesize = request.filesize(self.url)
        return await self._filesize

    @property
    def title(self) -> str:
        """Get title of video

        :rtype: str
        :returns:
            Youtube video title
        """
        return self._monostate.title or "Unknown YouTube Video Title"

    @property
    async def filesize_approx(self) -> int:
        """Get approximate filesize of the video

        Falls back to HTTP call if there is not sufficient information to approximate

        :rtype: int
        :returns: size of video in bytes
        """
        if self._monostate.duration and self.bitrate:
            bits_in_byte = 8
            return int((self._monostate.duration * self.bitrate) / bits_in_byte)

        return await self.filesize

    @property
    def expiration(self) -> datetime:
        expire = parse_qs(self.url.split("?")[1])["expire"][0]
        return datetime.utcfromtimestamp(int(expire))

    def __repr__(self) -> str:
        """Printable object representation.

        :rtype: str
        :returns:
            A string representation of a :class:`Stream <Stream>` object.
        """
        parts = ['itag="{s.itag}"', 'mime_type="{s.mime_type}"']
        if self.includes_video_track:
            parts.extend(['res="{s.resolution}"', 'fps="{s.fps}fps"'])
            if not self.is_adaptive:
                parts.extend(
                    ['vcodec="{s.video_codec}"', 'acodec="{s.audio_codec}"',]
                )
            else:
                parts.extend(['vcodec="{s.video_codec}"'])
        else:
            parts.extend(['abr="{s.abr}"', 'acodec="{s.audio_codec}"'])
        parts.extend(['progressive="{s.is_progressive}"', 'type="{s.type}"'])
        return f"<Stream: {' '.join(parts).format(s=self)}>"
