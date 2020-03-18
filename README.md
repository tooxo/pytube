# pytube3

## Table of Contents
  * [Intention of this fork](#Intention of this fork)
  * [Installation](#installation)
  * [Quick start](#quick-start)
  * [Features](#features)
  * [Usage](#usage)

## Intention of this fork

This fork is only the python interface of pytube, but written with asynchronicity in mind.
Some features like the commandline interface, downloading functions and captions were removed. 

## Installation

Download using pip via git.

```bash
$ pip install git+git://github.com/tooxo/pytube.git --upgrade
```
(Mac/homebrew users may need to use ``pip3``)


## Quick start
```
 >>> from pytube import YouTube
 >>> YouTube('https://youtu.be/9bZkp7q19f0').streams.get_highest_resolution().download()
 >>>
 >>> yt = YouTube('http://youtube.com/watch?v=9bZkp7q19f0')
 >>> yt.streams
  ... .filter(progressive=True, file_extension='mp4')
  ... .order_by('resolution')[-1]
  ... .download()
```
A GUI frontend for pytube3 is available at [YouTubeDownload](https://github.com/YouTubeDownload/YouTubeDownload)

## Features
  * Support for Both Progressive & DASH Streams
  * Support for downloading complete playlist
  * Easily Register ``on_download_progress`` & ``on_download_complete`` callbacks
  * Command-line Interfaced Included
  * Caption Track Support
  * Outputs Caption Tracks to .srt format (SubRip Subtitle)
  * Ability to Capture Thumbnail URL.
  * Extensively Documented Source Code
  * No Third-Party Dependencies

## Usage

Next, let's explore how we would view what video streams are available:

```
>>> yt = await YouTube.create('http://youtube.com/watch?v=9bZkp7q19f0')
>>> print(yt.streams)
 [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
 <Stream: itag="43" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp8.0" acodec="vorbis">,
 <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
 <Stream: itag="36" mime_type="video/3gpp" res="240p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
 <Stream: itag="17" mime_type="video/3gpp" res="144p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
 <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">,
 <Stream: itag="248" mime_type="video/webm" res="1080p" fps="30fps" vcodec="vp9">,
 <Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
 <Stream: itag="247" mime_type="video/webm" res="720p" fps="30fps" vcodec="vp9">,
 <Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401e">,
 <Stream: itag="244" mime_type="video/webm" res="480p" fps="30fps" vcodec="vp9">,
 <Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e">,
 <Stream: itag="243" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp9">,
 <Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015">,
 <Stream: itag="242" mime_type="video/webm" res="240p" fps="30fps" vcodec="vp9">,
 <Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c">,
 <Stream: itag="278" mime_type="video/webm" res="144p" fps="30fps" vcodec="vp9">,
 <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
 <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">,
 <Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus">,
 <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus">,
 <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus">]
```

### Selecting an itag

You may notice that some streams listed have both a video codec and audio codec, while others have just video or just audio, this is a result of YouTube supporting a streaming technique called Dynamic Adaptive Streaming over HTTP (DASH).

In the context of pytube, the implications are for the highest quality streams; you now need to download both the audio and video tracks and then post-process them with software like FFmpeg to merge them.

The legacy streams that contain the audio and video in a single file (referred to as "progressive download") are still available, but only for resolutions 720p and below.

To only view these progressive download streams:

```
 >>> yt.streams.filter(progressive=True)
  [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
  <Stream: itag="43" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp8.0" acodec="vorbis">,
  <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
  <Stream: itag="36" mime_type="video/3gpp" res="240p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
  <Stream: itag="17" mime_type="video/3gpp" res="144p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">]
```

Conversely, if you only want to see the DASH streams (also referred to as "adaptive") you can do:

```
>>> yt.streams.filter(adaptive=True)
 [<Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">,
  <Stream: itag="248" mime_type="video/webm" res="1080p" fps="30fps" vcodec="vp9">,
  <Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
  <Stream: itag="247" mime_type="video/webm" res="720p" fps="30fps" vcodec="vp9">,
  <Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401e">,
  <Stream: itag="244" mime_type="video/webm" res="480p" fps="30fps" vcodec="vp9">,
  <Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e">,
  <Stream: itag="243" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp9">,
  <Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015">,
  <Stream: itag="242" mime_type="video/webm" res="240p" fps="30fps" vcodec="vp9">,
  <Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c">,
  <Stream: itag="278" mime_type="video/webm" res="144p" fps="30fps" vcodec="vp9">,
  <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
  <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">,
  <Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus">,
  <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus">,
  <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus">]
```

### Playlists

You can also download a complete Youtube playlist:

```
>>> from pytube import Playlist
>>> playlist = await Playlist.create("https://www.youtube.com/playlist?list=PLynhp4cZEpTbRs_PYISQ8v_uwO0_mDg_X")
>>> for video in playlist:
>>> 	video.streams.get_highest_resolution().download()
```
This will download the highest progressive stream available (generally 720p) from the given playlist.

### Filtering

Pytube allows you to filter on every property available (see the documentation for the complete list), let's take a look at some of the most useful ones.

To list the audio only streams:

```
>>> yt.streams.filter(only_audio=True)
  [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
  <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">,
  <Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus">,
  <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus">,
  <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus">]
```

To list only ``mp4`` streams:

```
>>> yt.streams.filter(subtype='mp4')
 [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
  <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
  <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">,
  <Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
  <Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401e">,
  <Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e">,
  <Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015">,
  <Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c">,
  <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">]
```

Multiple filters can also be specified:

```
>>> yt.streams.filter(subtype='mp4', progressive=True)
>>> # this can also be expressed as:
>>> yt.streams.filter(subtype='mp4').filter(progressive=True)
  [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
  <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">]
```
You also have an interface to select streams by their itag, without needing to filter:

```
>>> yt.streams.get_by_itag(22)
  <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">
```

If you need to optimize for a specific feature, such as the "highest resolution" or "lowest average bitrate":

```
>>> yt.streams.filter(progressive=True).order_by('resolution').desc()
```
Note: Using ``order_by`` on a given attribute will filter out all streams missing that attribute.

#### Code Formatting

This project is linted with [pyflakes](https://github.com/PyCQA/pyflakes), formatted with [black](https://github.com/ambv/black), and typed with [mypy](https://mypy.readthedocs.io/en/latest/introduction.html)

#### Code of Conduct

Treat other people with helpfulness, gratitude, and consideration! See the [Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).
