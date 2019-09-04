import os
from invoke import task


@task
def challenge(ctx, title):
  from challenge import generate_challenge
  generate_challenge(title)


@task
def answer(ctx, title):
  from challenge import generate_answer
  generate_answer(title)


@task
def clean(ctx):
  from challenge import challenge_file, clip_range_file, clip_file
  for file_ in (challenge_file, clip_range_file, clip_file):
    if file_.exists():
      os.remove(file_)
