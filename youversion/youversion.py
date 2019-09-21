from typing import Dict, TypeVar, Optional, List, Tuple
from datetime import datetime
from os import path, getcwd
from shutil import copyfileobj

import requests


def day_of_year(dt: datetime) -> int:
    """
    Gets the day of the year from a datetime as an int

    :param dt: datetime to get day of the year from
    :return: day of the year as an int
    """
    return dt.timetuple().tm_yday


def day_of_year_from_timestamp(t: float) -> int:
    """
    Gets the day of the year from a timestamp as an int

    :param t: timestamp as a float
    :return: day of the year as an int
    """
    return day_of_year(datetime.fromtimestamp(t))


def day_of_the_year_from_iso_date(date_string: str) -> int:
    """
    Gets the day of the year from a ISO date string as returned from output of datetime.isoformat()

    :param date_string: An ISO date string as returned from output of datetime.isoformat()
    :return: day of the year as an int
    """
    return day_of_year(datetime.fromisoformat(date_string))


def current_day_of_year() -> int:
    """
    Gets the current day fo the year

    :return: day of the year as an int
    """
    return day_of_year(datetime.now())


def _slugify(value: str) -> str:
    """
    Converts the value to a slugified version reducing the str down to just
    alpha-numeric values and removing white-space

    :param value: value as a str
    :return: slugified version of the value
    """
    return ''.join(s for s in value if s.isalnum()).lower()


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


class DayOutOfBounds(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.day = kwargs.get('day', None)

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
    """
    Bible Verse
    """

    def __init__(self, bible_version: BibleVersion, json: dict):
        """
        Constructs a Verse

        :param bible_version: BibleVersion associated with the verse
        :param json: API response
        """
        self.bible_version = bible_version
        self.reference = json.get('human_reference', '')
        self.text = json.get('text', '')
        self.html = json.get('html', '')
        self.url = json.get('url', '')
        self.usfms = json.get('usfms', [])


class Image:
    """
    Verse Image
    """
    MAX_SIZE = 1280

    @staticmethod
    def _check_size(size: int):
        """
        Checks that the provided size is within the allowed bounds

        :param size: size to check as an int
        :return: None if valid otherwise InvalidImageSize is raised
        """
        if size > Image.MAX_SIZE:
            raise InvalidImageSize(size=size)

    def __init__(self, verse: Verse, json: dict):
        """
        Constructs an Image

        :param verse: Verse associated with the image
        :param json: API response
        """
        self.verse = verse
        self._url = f'https:{json.get("url", "")}'
        self.attribution = json.get('attribution', '')

    def url(self, width: int = MAX_SIZE, height: int = MAX_SIZE) -> str:
        """
        Gets an image url for the given width and height. InvalidImageSize raised If either the width or height
        is beyond the MAX_SIZE.

        :param width: width of the image. Defaults to MAX_SIZE
        :param height: height of the image. Defaults to MAX_SIZE
        :return: url as str
        """
        Image._check_size(width)
        Image._check_size(height)

        return self._url.replace('{width}', str(width)).replace('{height}', str(height))

    def square_url(self, size: int = MAX_SIZE) -> str:
        """
        Gets an image url for a square image of the given size
        :param size: size of the image as an int. Defaults to MAX_SIZE
        :return: url as a str
        """
        return self.url(size, size)

    def download(self, width: int = MAX_SIZE, height: int = MAX_SIZE, save_path: str = None) -> str:
        """
        Downloads the current image into the save_path

        :param width: image width as an int. Defaults to MAX_SIZE
        :param height: image height as an int. Defaults to MAX_SIZE
        :param save_path: full path to downloaded file including file name. Defaults the current directory
        :return: image path as str
        """
        image_url = self.url(width, height)
        image_path = save_path if save_path else path.join(getcwd(), f'{_slugify(self.verse.reference)}.jpg')

        with requests.get(image_url, stream=True) as response:
            response.raise_for_status()
            with open(image_path, 'wb') as file:
                response.raw.decode_content = True
                copyfileobj(response.raw, file)

        return image_path


class VerseOfTheDay:
    """
    Verse of the Day
    """

    def __init__(self, bible_version: BibleVersion, json: dict):
        """
        Constructs a Verse of the Day

        :param bible_version: BibleVersion associated with the verse
        :param json: API response
        """
        self.bible_version = bible_version
        self.day = json.get('day', None)
        self.verse = Verse(bible_version=self.bible_version, json=json.get('verse', {}))
        self.image = Image(verse=self.verse, json=json.get('image', {}))


BibleVersionOption = TypeVar('BibleVersionOption', str, BibleVersion)


class API:
    VERSION = '1.0'
    BASE_URL = f'https://developers.youversionapi.com/{VERSION}'

    def __init__(self, token: str, language: str = Language.English):
        """
        Constructs a new YouVersion API

        :param token: YouVersion Developer API token as a str
        :param language: One of the supported languages from youversion.Language.
               Defaults to youversion.Language.English
        """

        self._token = token
        self.language = language
        self.bible_version = BibleVersion.KJV()
        self._supported_bible_version = {}

    @property
    def language(self):
        """
        Gets the current language

        :return: language as a str
        """
        return self.__language

    @language.setter
    def language(self, language: str):
        """
        Sets the current language. Should be one of the supported
        languages found in youversion.Language. If the language is not
        one of the supported languages than an UnsupportedLanguage will be raised

        :param language: one of the supported Language tags
        """
        if language in Language.__dict__:
            self.__language = Language.__dict__.get(language)
        elif language in Language.__dict__.values():
            self.__language = language
        else:
            raise UnsupportedLanguage(language=language)

    @property
    def bible_version(self) -> Optional[BibleVersion]:
        """
        Gets the currently set Bible version
        :return: BibleVersion or None
        """
        return self.__bible_version

    @bible_version.setter
    def bible_version(self, bible_version: BibleVersionOption):
        """
        Sets the current Bible version

        :param bible_version: A valid BibleVersionOption which should be either a str or BibleVersion
        """
        if isinstance(bible_version, BibleVersion):
            self.__bible_version = bible_version
        elif isinstance(bible_version, str) and self.supports_bible_version(bible_version):
            self.__bible_version = self.get_bible_version(bible_version)
        else:
            raise InvalidBibleVersion(version=bible_version)

    @property
    def _header(self) -> Dict[str, str]:
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
    def bible_versions(self) -> Dict[str, BibleVersion]:
        """
        Gets the list of supported Bible versions

        :return: Dict mapping abbreviation to BibleVersion
        """
        if len(self._supported_bible_version) <= 0:
            versions = self._get('versions')
            for data in versions.get('data'):
                bible_version = BibleVersion(data)
                if bible_version.abbreviation not in self._supported_bible_version:
                    self._supported_bible_version.setdefault(bible_version.abbreviation, bible_version)

        return self._supported_bible_version

    def supports_bible_version(self, abbreviation: str) -> bool:
        """
        Checks to see if the given abbreviation is supported by the YouVersion API

        :param abbreviation: Bible version abbreviation
        :return: True is the abbreviation is supported otherwise False
        """
        try:
            self.get_bible_version(abbreviation)
            return True
        except InvalidBibleVersion:
            return False

    def get_bible_version(self, abbreviation: str) -> BibleVersion:
        """
        Gets the Bible version for the given abbreviation.

        If the abbreviation can't be found an InvalidBibleVersion will be raised
        :param abbreviation: Bible version abbreviation
        :return: BibleVersion
        """
        if abbreviation in self.bible_versions:
            return self._supported_bible_version[abbreviation]
        raise InvalidBibleVersion(version=abbreviation)

    def get_verse_of_the_day(self, day: int = current_day_of_year()) -> VerseOfTheDay:
        """
        Gets the verse of the day for the given day

        :param day: day as an int defaults to the current day of the year
        :return: VerseOfTheDay for the given day
        """

        if day < 1 or day > 366:
            raise DayOutOfBounds(day=day)

        return VerseOfTheDay(
            bible_version=self.bible_version,
            json=self._get(
                f'verse_of_the_day/{day}',
                params={
                    'version_id': self.bible_version.id
                }
            )
        )

    def get_all_verse_of_the_days(self, limit: int = 366, page: int = 1) -> Tuple[bool, int, Optional[List[VerseOfTheDay]]]:
        """
        Gets multiple verse of the day objects

        :param limit: Currently not used (see issue: https://github.com/lifechurch/youversion-public-api-docs/issues/7)
        :param page: Currently not used (see issue: https://github.com/lifechurch/youversion-public-api-docs/issues/7)
        :return: tuple[bool, int, list of VerseOfTheDay].
            bool indicates if another page is available, if results are paginated
            int the number of VerseOfTheDay objects contained in the response
            list of VerseOfTheDay objects
        """
        json = self._get('verse_of_the_day', params={'version_id': self.bible_version.id})
        if not json or 'data' not in json:
            return False, 0, None

        votds = [VerseOfTheDay(bible_version=self.bible_version, json=data) for data in json.get('data', [])]
        next_page = json.get('next_page', False)
        page_size = json.get('page_size', len(votds))

        return next_page, page_size, votds
