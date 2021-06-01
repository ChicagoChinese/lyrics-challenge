# Lyrics Challenge

## Prerequisites

```
brew install python3 pipenv
```

## Install

    pipenv install

## Commands

Activate project's virtualenv

    pipenv shell

Show all commands

    inv -l

Generate challenge

    inv challenge 要死就一定死在你手里

Clean output files

    inv clean

## Configuration

Create `settings.py`:

```python
MUSIC_DIR = '~/Music/'

NOTION_TOKEN = 'your token here'

TRANSLATION_DOC = 'https://www.notion.so/chicagochinese/Translations-f19fbfaa306340b18490fbdff9181993'

```

## Notes

This project uses the [notion-py library](https://github.com/jamalex/notion-py) to fetch data from Notion.

Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so

# Links

- [Notion API](https://developers.notion.com/)
- [Notion API Reference](https://developers.notion.com/reference/)
- [Notion: My Integrations](https://www.notion.so/my-integrations)
- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py)
