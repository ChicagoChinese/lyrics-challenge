# Lyrics Challenge

## Prerequisites

```
brew install python3 pipenv
```

## Install

```
pipenv install
```

## Commands

Generate exercise

```
python main.py 要死就一定死在你手里
```

Clean output files

```
rm clip-range.txt
rm clip.m4a
rm lyrics.txt
```

## Configuration

Create `settings.py`:

```python
MUSIC_DIR = '/Users/bobo/Music/'

NOTION_TOKEN = 'your token here'

TRANSLATION_DOC = 'https://www.notion.so/chicagochinese/Translations-f19fbfaa306340b18490fbdff9181993'

```
