# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    urlencode_postdata,
    std_headers,
)


class TestedIE(InfoExtractor):

    _VALID_URL = r'https?://(?:www\.)?tested\.com/premium/(?P<id>[0-9]+)'
    _LOGIN_URL = 'https://www.tested.com/auth/login/?next=/'
    _NETRC_MACHINE = 'tested'

    _TEST = {
        'url': 'http://www.tested.com/premium/754506-totally-unauthorized-commentary-spirited-away-2001/',
        'md5': 'TODO: md5 sum of the first 10241 bytes of the video file (use --test)',
        'info_dict': {
            'id': '42',
            'ext': 'mp4',
            'title': 'Totally Unauthorized Commentary: Spirited Away (2001)',
            'thumbnail': r're:^https?://.*\.jpg$',
            # TODO more properties, either as:
            # * A value
            # * MD5 checksum; start the string with md5:
            # * A regular expression; start the string with re:
            # * Any Python type (for example int or float)
        }
    }

    def _real_initialize(self):
        self._login()

    def _login(self):
        (username, password) = self._get_login_info()

        # TODO: Check if URL is premium and require login.
        if username is None:
            return

        headers = std_headers.copy()
        if 'Referer' not in headers:
            headers['Referer'] = self._LOGIN_URL

        login_request = self._download_webpage(
            self._LOGIN_URL, None,
            note='Logging in',
            data=urlencode_postdata({
              'username': username,
              'password': password,
              'next': '/'
            }),
            headers=headers)

        if not any(re.search(p, login_request) for p in (
                r'href="/auth/logout"',
                r'>Log Out<')):
            # FIXME: Extract login error messages.
            error = 'Unknown login error'
            if error:
                raise ExtractorError('Unable to login: %s' % error, expected=True)
            raise ExtractorError('Unable to log in')

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage, webpage_handle = self._download_webpage_handle(url, video_id)

        # Try to get video metadata from a helpful header the server gives us.
        whale_trail = webpage_handle.headers['Whale-Trail']
        video_info = {}
        if whale_trail:
            video_info = self._parse_json(whale_trail, video_id)
        else:
            raise ExtractorError('Missing metadata header')

        video_key = self._html_search_regex(r'OO\.Player\.create\(\'container\', \'(.+?)\',', webpage, 'video_key')
        playlist_url = "https://player.ooyala.com/player/all/%s.m3u8" % video_key
        print playlist_url

        return {
            'id': video_id,
            'title': video_info['object_title'],
            'description': self._og_search_description(webpage),
            'uploader': video_info['object_authors'][0],
            'formats': self._extract_m3u8_formats(playlist_url, video_id)
            # TODO more properties (see youtube_dl/extractor/common.py)
        }

