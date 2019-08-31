import sys
import subprocess
import json
from pathlib import Path

from notion.client import NotionClient

import settings

here = Path(__file__).parent
music_dir = Path(settings.MUSIC_DIR)
client = NotionClient(token_v2=settings.NOTION_TOKEN)
lyrics_file = here / 'lyrics.txt'
clip_range_file = here / 'clip-range.txt'
clip_file = here / 'clip.m4a'


def main():
  title = sys.argv[1]
  tracks = list(music_dir.glob(f'**/*{title}*.m4a'))

  if len(tracks) == 0:
    print('No tracks found')
  elif len(tracks) > 1:
    print('Found more than one track:')
    for track in tracks:
      print(track)
  else:
    process(tracks[0])


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

  # Get translated english lyrics
  fetch_lyrics(tags['title'])

  # todo: Create audio clip
  create_audio_clip(track)

  # Print Chinese lyrics
  lyrics = tags['lyrics'].replace('\r', '\n')
  print(f'\nOriginal lyrics:\n{lyrics}\n')


def fetch_lyrics(title):
  if lyrics_file.exists() and clip_range_file.exists():
    return

  index_page = client.get_block(settings.TRANSLATION_INDEX)

  matching_rows = [
    row
    for row in index_page.collection.get_rows()
    if row.chinese_title == title]

  if len(matching_rows) == 0:
    print(f'No translation named {title}')
    return

  row = matching_rows[0]

  with clip_range_file.open('w') as fp:
    fp.write(row.clip_range + '\n')

  print(f'Generated {clip_range_file}')

  tv = client.get_collection_view(row.translation)

  translation_map = {}

  with lyrics_file.open('w') as fp:
    for row in tv.default_query().execute():
      if row.english:
        translation_map[row.chinese] = row.english

      line = row.english if row.english != '' \
        else translation_map.get(row.chinese, '')
      fp.write(line + '\n')

  print(f'Generated {lyrics_file}')


def create_audio_clip(track):
  if clip_file.exists():
    return

  start, stop = clip_range_file.read_text().strip().split('-')

  cmd = [
    'ffmpeg',
    '-i', str(track),
    '-ss', start.strip(),
    '-to', stop.strip(),
    '-acodec', 'copy',
    '-map_metadata', '-1',    # strip metadata
    str(clip_file)
  ]
  subprocess.call(cmd)

  print(f'Generated {clip_file}')


if __name__ == '__main__':
  main()
