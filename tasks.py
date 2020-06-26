import os
from pathlib import Path

from invoke import task


@task
def challenge(ctx, url):
    """
    Generate challenge for pasting into ChineseForums.com
    """
    from challenge import generate_challenge
    generate_challenge(url)


@task
def clean(ctx):
    """
    Clean files
    """
    from challenge import challenge_file, clip_file
    for file_ in (challenge_file, clip_file):
        if file_.exists():
            os.remove(file_)

    for file_ in Path('.').glob('*.csv'):
        os.remove(file_)


@task
def csv(ctx, url):
    """
    Export lyrics page to CSV
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
