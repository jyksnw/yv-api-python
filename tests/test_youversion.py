import os
import pytest
import unittest

import youversion

from requests import HTTPError

YOUVERSION_API_TOKEN = os.getenv('YOUVERSION_API_TOKEN', None)
if not YOUVERSION_API_TOKEN:
    raise ValueError('YOUVERSION_API_TOKEN')


class APITest(unittest.TestCase):

    def setUp(self) -> None:
        self.client = youversion.API(YOUVERSION_API_TOKEN)

    def test_default_language(self):
        assert self.client.language == youversion.Language.English

    def test_set_valid_language(self):
        self.client.language = youversion.Language.Spanish
        assert self.client.language == youversion.Language.Spanish

    def test_set_valid_language_abbreviation(self):
        self.client.language = 'es'
        assert self.client.language == youversion.Language.Spanish

    def test_set_invalid_language(self):
        with pytest.raises(youversion.UnsupportedLanguage):
            self.client.language = 'BAD_LANG'

    def test_header_accepts_json(self):
        header = self.client._header
        assert 'accept' in header
        assert header['accept'] == 'application/json'

    def test_header_contains_token(self):
        header = self.client._header
        assert 'x-youversion-developer-token' in header
        assert header['x-youversion-developer-token'] == YOUVERSION_API_TOKEN

    def test_header_contains_language(self):
        header = self.client._header
        assert 'accept-language' in header
        assert header['accept-language'] == youversion.Language.English

    def test_invalid__get_raises(self):
        with pytest.raises(HTTPError):
            self.client._get('not_a_valid_resource')

    def test_default_bible_version(self):
        bible_version = self.client.bible_version
        assert bible_version.id is not None
        assert bible_version.id == youversion.BibleVersion.KJV().id

    def test_valid_bible_version(self):
        self.client.bible_version = self.client.bible_versions['ASV']
        assert self.client.bible_version.abbreviation == 'ASV'

    def test_valid_bible_version_by_abbreviation(self):
        self.client.bible_version = 'ASV'
        assert self.client.bible_version.abbreviation == 'ASV'

    def test_invalid_bible_version(self):
        with pytest.raises(youversion.InvalidBibleVersion):
            self.client.bible_version = 'BAD_VERSION'

    def test_supports_valid_bible_version(self):
        assert self.client.supports_bible_version('ASV') is True

    def test_does_not_support_invalid_bible_version(self):
        assert self.client.supports_bible_version('BAD_VERSION') is False

    def test_get_bible_versions(self):
        assert len(self.client.bible_versions) > 0

    def test_get_bible_versions_contains_KJV(self):
        assert 'KJV' in self.client.bible_versions

    def test_get_valid_bible_version(self):
        assert self.client.get_bible_version('ASV') is not None

    def test_get_invalid_bible_version(self):
        with pytest.raises(youversion.InvalidBibleVersion):
            self.client.get_bible_version('BAD_VERSION')

    def test_get_verse_of_the_day(self):
        assert self.client.get_verse_of_the_day() is not None

    def test_get_verse_of_the_day_returns_request_day(self):
        assert self.client.get_verse_of_the_day(day=90).day == 90

    def test_get_verse_of_the_day_bible_version(self):
        self.client.bible_version = 'ASV'
        assert self.client.get_verse_of_the_day().bible_version.abbreviation == 'ASV'

    def test_get_verse_of_the_day_contains_verse(self):
        votd = self.client.get_verse_of_the_day()
        assert votd.verse is not None
        assert votd.verse.text is not None and votd.verse.text != ''
        assert votd.verse.url is not None and votd.verse.url != ''

    def test_get_verse_of_the_day_verse_bible_version(self):
        self.client.bible_version = 'ASV'
        assert self.client.get_verse_of_the_day().verse.bible_version.abbreviation == 'ASV'

    def test_get_verse_of_the_day_contains_image(self):
        votd = self.client.get_verse_of_the_day()
        assert votd.image is not None
        assert votd.image.verse is not None
        assert votd.image._url is not None and votd.image._url != ''
