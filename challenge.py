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
clip_file = here / 'clip.mp3'


def generate_challenge(url):
    page = client.get_block(url)
    view = client.get_collection_view(url, collection=page.collection)

    track = get_track(page.title)
    if not track:
        print(f'Could not find {track}')
        return

    print(f'Processing {track}\n')
    meta = get_page_meta(page)
    create_audio_clip(track, meta['clip_range'])
    generate_challenge_file(view, meta)


def add_lyrics(title):
    track = get_track(title)
    if track is None:
        return

    print(track)

    root = client.get_block(settings.LYRICS_ROOT)

    meta = get_track_meta(track)
    lyrics = meta.get('lyrics', '')
    if lyrics == '':
        lyrics = meta.get('lyrics-eng', '')

    lyrics = [
        'artist = ' + meta['artist'],
        'link = ' + meta['comment'],
        '===',
    ] + lyrics.split('\r')

    child = root.children.add_new(PageBlock, title=meta['title'])
    for line in lyrics:
        child.children.add_new(TextBlock, title=line)
        print(line)

    print(f'\nLyrics published to {child.get_browseable_url()}')


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


def get_page_meta(page):
    lines = page.description.splitlines()
    meta = {}
    for line in lines:
        key, value = line.split('=', 1)
        key = key.strip()
        meta[key] = value.strip()

    meta['title'] = page.title
    meta['url'] = page.get_browseable_url()
    return meta


def markdown(text):
    # Strip off <p></p>:
    return markdown2.markdown(text)[3:-5]


def generate_challenge_file(view, meta):
    meta['link'] = markdown(meta['link'])

    chinese_lyrics = []
    english_lyrics = []

    translation_map = {'': ''}
    english_lyrics = []

    for row in view.default_query().execute():
        chinese_lyrics.append(row.chinese)

        if row.english:
            translation_map[row.chinese] = row.english

        line = row.english if row.english != '' \
            else translation_map.get(row.chinese, row.chinese)
        english_lyrics.append(line)

    with challenge_file.open('w') as fp:
        related_works = meta.get('related_works')
        if related_works is not None:

            related_works = markdown(related_works)

        html = env.get_template('challenge.html').render(
            song=meta, english_lyrics=english_lyrics, chinese_lyrics=chinese_lyrics,
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


def create_audio_clip(track, clip_range_text):
    if clip_file.exists():
        return

    try:
        start, stop = clip_range_text.strip().split('-')
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
