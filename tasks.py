import os
from pathlib import Path

from invoke import task


@task
def challenge(ctx, title):
  """
  Generate challenge for paste into ChineseForums.com
  """
  from challenge import generate_challenge
  generate_challenge(title)


@task
def clean(ctx):
  """
  Clean files
  """
  from challenge import challenge_file, clip_range_file, clip_file
  for file_ in (challenge_file, clip_range_file, clip_file):
    if file_.exists():
      os.remove(file_)

  for file_ in Path('.').glob('*.csv'):
    os.remove(file_)


@task
def csv(ctx, url):
  """
  Generate lyrics CSV file for import into Notion
  """
  from generate import generate_lyrics_csv_file
  generate_lyrics_csv_file(url)


@task
def lyrics(ctx, title):
  """
  Add lyrics into Notion
  """
  from challenge import add_lyrics
  add_lyrics(title)
