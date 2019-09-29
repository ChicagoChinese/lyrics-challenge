import subprocess
import json
from pathlib import Path

import markdown2
from notion.client import NotionClient
from notion.block import PageBlock, TextBlock
from jinja2 import Environment, FileSystemLoader, select_autoescape

import settings


env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


here = Path(__file__).parent
music_dir = Path(settings.MUSIC_DIR)
client = NotionClient(token_v2=settings.NOTION_TOKEN)
challenge_file = here / 'challenge.html'
answer_file = here / 'answer.html'
clip_range_file = here / 'clip-range.txt'
clip_file = here / 'clip.mp3'


def generate_challenge(title):
  track = get_track(title)
  if not track:
    return

  print(f'Processing {track}\n')
  tags = get_track_meta(track)
  row = fetch_song_row(tags['title'])
  generate_clip_range_file(row)
  create_audio_clip(track)
  generate_challenge_file(row)


def add_lyrics(title):
  track = get_track(title)
  if track is None:
    return

  print(track)

  root = client.get_block(settings.LYRICS_ROOT)

  meta = get_track_meta(track)
  lyrics = meta.get('lyrics', '').split('\r')

  child = root.children.add_new(PageBlock, title=meta['title'])
  for line in lyrics:
    child.children.add_new(TextBlock, title=line)
    print(line)


def get_track(title):
  tracks = list(music_dir.glob(f'**/*{title}*.m4a'))
  tracks += list(music_dir.glob(f'**/*{title}*.mp3'))

  if len(tracks) == 0:
    print('No tracks found')
    return None
  elif len(tracks) > 1:
    print('Found more than one track:')
    for i, track in enumerate(tracks, 1):
      print(f'{i}. {track}')
    choice = int(input('Which one do you want? '))
    return tracks[choice - 1]
  else:
    return tracks[0]


def get_track_meta(track):
  cmd = [
    'ffprobe',
    '-v', 'quiet',
    str(track),
    '-show_format',
    '-print_format', 'json',
  ]
  meta = json.loads(subprocess.check_output(cmd))
  return meta['format']['tags']


def generate_clip_range_file(row):
  if clip_range_file.exists():
    return

  with clip_range_file.open('w') as fp:
    fp.write(row.clip_range + '\n')

  print(f'Generated {clip_range_file}')


def generate_challenge_file(song):
  if challenge_file.exists():
    return

  english_lyrics = []

  if song.translation == '':
    print(f'No translation found for {title}')
  else:
    tv = client.get_collection_view(song.translation)
    translation_map = {'': ''}
    english_lyrics = []

    for row in tv.default_query().execute():
      if row.english:
        translation_map[row.chinese] = row.english

      line = row.english if row.english != '' \
        else translation_map.get(row.chinese, f'not found: "{row.chinese}"')
      english_lyrics.append(line)

  with challenge_file.open('w') as fp:
    chinese_lyrics = song.lyrics.splitlines()
    # Strip off <p></p>:
    related_works = markdown2.markdown(song.related_works)[3:-5]

    html = env.get_template('challenge.html').render(
      song=song, english_lyrics=english_lyrics, chinese_lyrics=chinese_lyrics,
      related_works=related_works)

    fp.write(html)

  print(f'Generated {challenge_file}')



def fetch_song_row(title):
  index_page = client.get_block(settings.CHALLENGE_TABLE)

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
