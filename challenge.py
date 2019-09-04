import subprocess
import json
from pathlib import Path

from notion.client import NotionClient
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

import settings

here = Path(__file__).parent
music_dir = Path(settings.MUSIC_DIR)
client = NotionClient(token_v2=settings.NOTION_TOKEN)
challenge_file = here / 'challenge.html'
answer_file = here / 'answer.html'
clip_range_file = here / 'clip-range.txt'
clip_file = here / 'clip.mp3'


def generate_challenge(title):
  track = get_track(title)
  process(track)


def generate_answer(title):
  track = get_track(title)

  row = get_song_row(title)

  with answer_file.open('w') as fp:
    lyrics = row.lyrics.splitlines()
    html = env.get_template('answer.html').render(song=row, lyrics=lyrics)
    fp.write(html)


def get_track(title):
  tracks = list(music_dir.glob(f'**/*{title}*.m4a'))
  if len(tracks) == 0:
    tracks = list(music_dir.glob(f'**/*{title}*.mp3'))

  if len(tracks) == 0:
    print('No tracks found')
    return None
  elif len(tracks) > 1:
    print('Found more than one track:')
    for i, track in enumerate(tracks, 1):
      print(f'{i}. {track}')
    choice = int(input('Which one do you want? '))
    return tracks[choice -1]
  else:
    return tracks[0]


def process(track):
  print(f'Processing {track}\n')

  cmd = [
    'ffprobe',
    '-v', 'quiet',
    str(track),
    '-show_format',
    '-print_format', 'json',
  ]
  meta = json.loads(subprocess.check_output(cmd))
  tags = meta['format']['tags']

  fetch_lyrics(tags['title'])

  create_audio_clip(track)

  # Print Chinese lyrics
  # lyrics = tags.get('lyrics')
  # if not lyrics:
  #   lyrics = tags.get('lyrics-eng', '')
  # lyrics = lyrics.replace('\r', '\n')
  # print(f'\nOriginal lyrics:\n{lyrics}\n')


def fetch_lyrics(title):
  if challenge_file.exists() and clip_range_file.exists():
    return

  index_page = client.get_block(settings.TRANSLATION_INDEX)

  row = get_song_row(title)

  with clip_range_file.open('w') as fp:
    fp.write(row.clip_range + '\n')

  print(f'Generated {clip_range_file}')

  if row.translation == '':
    print(f'No translation found for {title}')
    return

  print(row.english_title + '\n')

  tv = client.get_collection_view(row.translation)

  translation_map = {'': ''}

  with challenge_file.open('w') as fp:
    lyrics = []
    for row in tv.default_query().execute():
      if row.english:
        translation_map[row.chinese] = row.english

      line = row.english if row.english != '' \
        else translation_map.get(row.chinese, 'n/a')
      lyrics.append(line)

    html = env.get_template('challenge.html').render(lyrics=lyrics)
    fp.write(html)

  print(f'Generated {challenge_file}')


def get_song_row(title):
  index_page = client.get_block(settings.TRANSLATION_INDEX)

  matching_rows = [
    row
    for row in index_page.collection.get_rows()
    if row.chinese_title == title]

  if len(matching_rows) == 0:
    print(f'No entry found for {title}')
    return None
  else:
    return matching_rows[0]


def create_audio_clip(track):
  if clip_file.exists():
    return

  try:
    start, stop = clip_range_file.read_text().strip().split('-')
  except Exception as ex:
    print(f'Invalid clip range: {ex}')
    return

  cmd = [
    'ffmpeg',
    '-i', str(track),
    '-ss', start.strip(),
    '-to', stop.strip(),
    '-map_metadata', '-1',    # strip metadata
    # '-acodec', 'copy',      # can't be used when converting between formats
    str(clip_file)
  ]
  subprocess.call(cmd)

  print(f'Generated {clip_file}')


if __name__ == '__main__':
  main()
