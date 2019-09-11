from datetime import datetime
from os import path, getcwd
from shutil import copyfileobj

import requests


def _day_of_year(dt: datetime):
    return dt.timetuple().tm_yday


def _current_day_of_year():
    return _day_of_year(datetime.now())


def _timestamp_day_of_year(t: float):
    return _day_of_year(datetime.fromtimestamp(t))


def _isodate_day_of_year(date_string):
    return _day_of_year(datetime.fromisoformat(date_string))


def _slugify(value):
    return "".join(s for s in value if s.isalnum())


class UnsupportedLanguage(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.language = kwargs.get('language', '')


class InvalidImageSize(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.size = kwargs.get('size', None)


class InvalidBibleVersion(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.version = kwargs.get('version', None)


class Language:
    """
    Supported API languages
    """

    Afrikaans = 'af'
    Chinese_Simplified = 'zh_CN'
    Chinese_Traditional = 'zh_TW'
    Dutch = 'nl'
    English = 'en'
    French = 'fr'
    German = 'de'
    Greek = 'el'
    Indonesian = 'id'
    Italian = 'it'
    Khmer = 'km'
    Korean = 'ko'
    Portuguese = 'pt'
    Romanian = 'ro'
    Russian = 'ru'
    Spanish = 'es'
    Swahili = 'sw'
    Swedish = 'sv'
    Tagalog = 'tl'
    Filipino = 'tl'
    Ukrainian = 'uk'
    Vietnamese = 'vi'
    Zulu = 'zu'


class BibleVersion:
    """
    Contains information about a Bible version
    """

    @staticmethod
    def KJV():
        """
        Cached King James BibleVersion

        :return: BibleVersion for King James Version
        """
        return BibleVersion({
            'id': 1,
            'title': 'King James Version',
            'abbreviation': 'KJV',
            'copyright_short': 'Crown Copyright in UK',
            'local_title': 'King James Version',
            'local_abbreviation': 'KJV'
        })

    def __init__(self, json: dict):
        self.id = json.get('id', None)
        self.title = json.get('title', '')
        self.abbreviation = json.get('abbreviation', '')
        self.local_title = json.get('local_title', '')
        self.local_abbreviation = json.get('local_abbreviation', '')
        self.copyright = json.get('copyright_short', '')


class Verse:

    def __init__(self, bible_version: BibleVersion, json: dict):
        self.bible_version = bible_version
        self.reference = json.get('human_reference', '')
        self.text = json.get('text', '')
        self.html = json.get('html', '')
        self.url = json.get('url', '')
        self.usfms = json.get('usfms', [])


class Image:
    MAX_SIZE = 1280

    @staticmethod
    def _check_size(size: int):
        if size > Image.MAX_SIZE:
            raise InvalidImageSize(size=size)

    def __init__(self, verse: Verse, json: dict):
        self.verse = verse
        self._url = f'https:{json.get("url", "")}'
        self.attribution = json.get('attribution', '')

    def url(self, width: int = MAX_SIZE, height: int = MAX_SIZE):
        Image._check_size(width)
        Image._check_size(height)

        return self._url.replace('{width}', str(width)).replace('{height}', str(height))

    def square_url(self, size: int = MAX_SIZE):
        return self.url(size, size)

    def download(self, width: int = MAX_SIZE, height: int = MAX_SIZE, save_path: str = None):
        image_url = self.url(width, height)
        image_path = save_path if save_path else path.join(getcwd(), f'{_slugify(self.verse.reference)}.jpg')

        with requests.get(image_url, stream=True) as response:
            response.raise_for_status()
            with open(image_path, 'wb') as file:
                response.raw.decode_content = True
                copyfileobj(response.raw, file)

        return image_path


class VOTD:
    def __init__(self, bible_version: BibleVersion, json: dict):
        self.bible_version = bible_version
        self.day = json.get('day', None)
        self.verse = Verse(bible_version=self.bible_version, json=json.get('verse', {}))
        self.image = Image(verse=self.verse, json=json.get('image', {}))


class API:
    VERSION = '1.0'
    BASE_URL = f'https://developers.youversionapi.com/{VERSION}'

    def __init__(self, token: str = '', language: str = Language.English):
        self._token = token
        self.language = language
        self.bible_version = BibleVersion.KJV()
        self._supported_bible_version = {}

    @property
    def language(self):
        return self.__language

    @language.setter
    def language(self, language: str):
        if language in Language.__dict__:
            self.__language = Language.__dict__.get(language)
        elif language in Language.__dict__.values():
            self.__language = language
        else:
            raise UnsupportedLanguage(language=language)

    @property
    def bible_version(self):
        return self.__bible_version

    @bible_version.setter
    def bible_version(self, bible_version):
        if type(bible_version) is BibleVersion:
            self.__bible_version = bible_version
        elif type(bible_version) is str and self.supports_bible_version(bible_version):
            self.__bible_version = self.get_bible_version(bible_version)
        else:
            raise InvalidBibleVersion(version=bible_version)

    @property
    def _header(self):
        return {
            "accept": "application/json",
            "x-youversion-developer-token": self._token,
            "accept-language": self.language,
        }

    def _get(self, resource: str, *args, **kwargs):
        """
        Gets the requested resource from the API

        A error will be thrown if the request is invalid

        :param resource: resource path
        :return: json response
        """

        url = path.join(API.BASE_URL, resource)
        response = requests.get(url, headers=self._header, **kwargs)

        if response.ok:
            return response.json()

        response.raise_for_status()

    @property
    def bible_versions(self):
        if len(self._supported_bible_version) <= 0:
            versions = self._get('versions')
            for data in versions.get('data'):
                bible_version = BibleVersion(data)
                if bible_version.abbreviation not in self._supported_bible_version:
                    self._supported_bible_version.setdefault(bible_version.abbreviation, bible_version)

        return self._supported_bible_version

    def supports_bible_version(self, abbreviation: str):
        try:
            self.get_bible_version(abbreviation)
            return True
        except InvalidBibleVersion:
            return False

    def get_bible_version(self, abbreviation: str):
        if abbreviation in self._supported_bible_version:
            return self._supported_bible_version[abbreviation]

        bible_version = [version for version in self.bible_versions if abbreviation == version.abbreviation]
        if not bible_version:
            raise InvalidBibleVersion(version=abbreviation)

        return bible_version[0]

    def get_verse_of_the_day(self, day=_current_day_of_year()):
        return VOTD(
            bible_version=self.bible_version,
            json=self._get(
                f'verse_of_the_day/{day}',
                params={
                    'version_id': self.bible_version.id
                }
            )
        )
