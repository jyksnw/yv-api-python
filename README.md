[![Known Vulnerabilities](https://snyk.io//test/github/jyksnw/yv-api-python/badge.svg?targetFile=requirements.txt)](https://snyk.io//test/github/jyksnw/yv-api-python?targetFile=requirements.txt)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8828c30b95a841b7b0052977c243fdde)](https://www.codacy.com/manual/jyksnw/yv-api-python?utm_source=github.com&utm_medium=referral&utm_content=jyksnw/yv-api-python&utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/8828c30b95a841b7b0052977c243fdde)](https://www.codacy.com/manual/jyksnw/yv-api-python?utm_source=github.com&utm_medium=referral&utm_content=jyksnw/yv-api-python&utm_campaign=Badge_Coverage)
[![Build Status](https://travis-ci.org/jyksnw/yv-api-python.svg?branch=master)](https://travis-ci.org/jyksnw/yv-api-python)

# YouVersion API Client

YouVersion Public API Client. This project has no affiliation with YouVersion or Life.Church.

-   [API Documentation](https://yv-public-api-docs.netlify.com/index.html)
-   Client Documentation (coming soon!)

## Installation

`pip install youversion`

## Usage

A YouVersion API Developer Token will be needed. Information about obtaining an API token can be found in the [YouVersion API documentation](https://yv-public-api-docs.netlify.com/getting-started.html#getting-an-api-token)

```python
import youversion as yv
import webbrowser

YV_TOKEN = 'YouVersion API Developer Token'
YV_LANG = yv.Language.English

api = yv.API(YV_TOKEN, YV_LANG)

print(api.bible_versions)

# Sets the Bible version (defaults to KJV)
api.bible_version = 'KJV'

# Or use the BibleVersion object
api.bible_version = api.get_bible_version('ASV')

# Gets the current verse of the day
votd = api.get_verse_of_the_day()

# Print the verse of the day verse text
print(votd.verse.text)

# Downloads the verse of the day image
votd.image.download()

# Open the verse of the day square image in a browser
webbrowser.open_new_tab(votd.image.square_url(size=256))
```

## Development

Information about how to get setup for development and contribution is coming soon.
