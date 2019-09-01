import os
from invoke import task


@task
def challenge(ctx, title):
  from challenge import generate_challenge
  generate_challenge(title)


@task
def clean(ctx):
  from challenge import lyrics_file, clip_range_file, clip_file
  os.remove(lyrics_file)
  os.remove(clip_range_file)
  os.remove(clip_file)
