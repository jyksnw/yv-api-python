import os
import tempfile
import pytest
import unittest
from datetime import datetime

import youversion

from requests import HTTPError

YOUVERSION_API_TOKEN = os.getenv('YOUVERSION_API_TOKEN', None)
if not YOUVERSION_API_TOKEN:
    raise ValueError('YOUVERSION_API_TOKEN')


def test_day_of_year():
    dt = datetime.fromtimestamp(1568416679.74593)
    if not youversion.day_of_year(dt) == 256:
        raise AssertionError()


def test_day_of_year_from_timestamp():
    if not youversion.day_of_year_from_timestamp(1568416679.74593) == 256:
        raise AssertionError()


def test_day_of_the_year_from_iso_date():
    if not youversion.day_of_the_year_from_iso_date('2019-09-13T19:21:06.010865') == 256:
        raise AssertionError()


def test_current_day_of_year():
    current_day = datetime.now().timetuple().tm_yday
    if not youversion.current_day_of_year() == current_day:
        raise AssertionError()


class ImageTest(unittest.TestCase):

    def setUp(self) -> None:
        self.client = youversion.API(YOUVERSION_API_TOKEN)

    def test_image_valid_url(self):
        votd = self.client.get_verse_of_the_day()
        url = votd.image.url(width=1, height=1)

        if not url or url == '':
            raise AssertionError()

    def test_image_invalid_width_url(self):
        votd = self.client.get_verse_of_the_day()
        with pytest.raises(youversion.InvalidImageSize):
            votd.image.url(width=youversion.Image.MAX_SIZE + 1, height=1)

    def test_image_invalid_height_url(self):
        votd = self.client.get_verse_of_the_day()
        with pytest.raises(youversion.InvalidImageSize):
            votd.image.url(width=1, height=youversion.Image.MAX_SIZE + 1)

    def test_image_valid_square_url(self):
        votd = self.client.get_verse_of_the_day()
        url = votd.image.square_url(size=1)

        if not url or url == '':
            raise AssertionError()

    def test_image_invalid_square_url(self):
        votd = self.client.get_verse_of_the_day()
        with pytest.raises(youversion.InvalidImageSize):
            votd.image.square_url(size=youversion.Image.MAX_SIZE + 1)

    def test_image_download_local_path(self):
        votd = self.client.get_verse_of_the_day()
        actual_save_path = None

        try:
            actual_save_path = votd.image.download(width=1, height=1)
            if not actual_save_path or actual_save_path == '' or not os.path.exists(actual_save_path):
                raise AssertionError()
        finally:
            if actual_save_path:
                os.remove(actual_save_path)

    def test_image_download_provided_path(self):
        _, save_path = tempfile.mkstemp()
        votd = self.client.get_verse_of_the_day()
        actual_save_path = None

        try:
            actual_save_path = votd.image.download(width=1, height=1, save_path=save_path)
            if not actual_save_path or actual_save_path == '' or not os.path.exists(actual_save_path):
                raise AssertionError()

            if not actual_save_path == save_path:
                raise AssertionError()
        finally:
            if actual_save_path:
                os.remove(actual_save_path)

            if os.path.exists(save_path):
                os.remove(save_path)


class APITest(unittest.TestCase):

    def setUp(self) -> None:
        self.client = youversion.API(YOUVERSION_API_TOKEN)

    def test_default_language(self):
        if not self.client.language == youversion.Language.English:
            raise AssertionError()

    def test_set_valid_language(self):
        self.client.language = youversion.Language.Spanish
        if not self.client.language == youversion.Language.Spanish:
            raise AssertionError()

    def test_set_valid_language_abbreviation(self):
        self.client.language = 'es'
        if not self.client.language == youversion.Language.Spanish:
            raise AssertionError()

    def test_set_valid_language_name(self):
        self.client.language = 'Spanish'
        if not self.client.language == youversion.Language.Spanish:
            raise AssertionError()

    def test_set_invalid_language(self):
        with pytest.raises(youversion.UnsupportedLanguage):
            self.client.language = 'BAD_LANG'

    def test_header_accepts_json(self):
        header = self.client._header
        if 'accept' not in header:
            raise AssertionError()
        if not header['accept'] == 'application/json':
            raise AssertionError()

    def test_header_contains_token(self):
        header = self.client._header
        if 'x-youversion-developer-token' not in header:
            raise AssertionError()
        if not header['x-youversion-developer-token'] == YOUVERSION_API_TOKEN:
            raise AssertionError()

    def test_header_contains_language(self):
        header = self.client._header
        if 'accept-language' not in header:
            raise AssertionError()
        if not header['accept-language'] == youversion.Language.English:
            raise AssertionError()

    def test_invalid__get_raises(self):
        with pytest.raises(HTTPError):
            self.client._get('not_a_valid_resource')

    def test_default_bible_version(self):
        bible_version = self.client.bible_version
        if bible_version.id is None:
            raise AssertionError()
        if not bible_version.id == youversion.BibleVersion.KJV().id:
            raise AssertionError()

    def test_valid_bible_version(self):
        self.client.bible_version = self.client.bible_versions['ASV']
        if not self.client.bible_version.abbreviation == 'ASV':
            raise AssertionError()

    def test_valid_bible_version_by_abbreviation(self):
        self.client.bible_version = 'ASV'
        if not self.client.bible_version.abbreviation == 'ASV':
            raise AssertionError()

    def test_invalid_bible_version(self):
        with pytest.raises(youversion.InvalidBibleVersion):
            self.client.bible_version = 'BAD_VERSION'

    def test_supports_valid_bible_version(self):
        if self.client.supports_bible_version('ASV') is False:
            raise AssertionError()

    def test_does_not_support_invalid_bible_version(self):
        if self.client.supports_bible_version('BAD_VERSION') is True:
            raise AssertionError()

    def test_get_bible_versions(self):
        if len(self.client.bible_versions) <= 0:
            raise AssertionError()

    def test_get_bible_versions_contains_KJV(self):
        if 'KJV' not in self.client.bible_versions:
            raise AssertionError()

    def test_get_valid_bible_version(self):
        if self.client.get_bible_version('ASV') is None:
            raise AssertionError()

    def test_get_invalid_bible_version(self):
        with pytest.raises(youversion.InvalidBibleVersion):
            self.client.get_bible_version('BAD_VERSION')

    def test_get_verse_of_the_day(self):
        if self.client.get_verse_of_the_day() is None:
            raise AssertionError()

    def test_get_verse_of_the_day_invalid_day(self):
        with pytest.raises(youversion.DayOutOfBounds):
            self.client.get_verse_of_the_day(day=-1)

        with pytest.raises(youversion.DayOutOfBounds):
            self.client.get_verse_of_the_day(day=367)

    def test_get_verse_of_the_day_returns_request_day(self):
        if not self.client.get_verse_of_the_day(day=90).day == 90:
            raise AssertionError()

    def test_get_verse_of_the_day_bible_version(self):
        self.client.bible_version = 'ASV'
        if not self.client.get_verse_of_the_day().bible_version.abbreviation == 'ASV':
            raise AssertionError()

    def test_get_verse_of_the_day_contains_verse(self):
        votd = self.client.get_verse_of_the_day()
        if votd.verse is None:
            raise AssertionError()
        if votd.verse.text is None or votd.verse.text == '':
            raise AssertionError()
        if votd.verse.url is None or votd.verse.url == '':
            raise AssertionError()

    def test_get_verse_of_the_day_verse_bible_version(self):
        self.client.bible_version = 'ASV'
        if not self.client.get_verse_of_the_day().verse.bible_version.abbreviation == 'ASV':
            raise AssertionError()

    def test_get_verse_of_the_day_contains_image(self):
        votd = self.client.get_verse_of_the_day()
        if votd.image is None:
            raise AssertionError()
        if votd.image.verse is None:
            raise AssertionError()
        if votd.image._url is None or votd.image._url == '':
            raise AssertionError()

    def test_get_all_verse_of_the_days(self):
        more_data, size, votds = self.client.get_all_verse_of_the_days()
        if more_data:
            # Should have received all data
            raise AssertionError()
        if size < 365 or size > 366:
            # Should be 365 or 366 responses
            raise AssertionError()
        if votds is None or len(votds) != size:
            raise AssertionError()
