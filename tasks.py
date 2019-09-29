import os
from pathlib import Path

from invoke import task


@task
def challenge(ctx, title):
  from challenge import generate_challenge
  generate_challenge(title)


@task
def clean(ctx):
  from challenge import challenge_file, clip_range_file, clip_file
  for file_ in (challenge_file, clip_range_file, clip_file):
    if file_.exists():
      os.remove(file_)

  for file_ in Path('.').glob('*.csv'):
    os.remove(file_)


@task
def csv(ctx, url):
  from generate import generate_lyrics_csv_file
  generate_lyrics_csv_file(url)


@task
def lyrics(ctx, title):
  from challenge import add_lyrics
  add_lyrics(title)
