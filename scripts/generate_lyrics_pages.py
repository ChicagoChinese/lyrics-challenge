"""
PYTHONPATH=. python scripts/generate_lyrics_pages.py

"""
import json
from pathlib import Path
import time

from notion.client import NotionClient
from notion.block import PageBlock, TextBlock

import settings
import challenge


if __name__ == '__main__':
  tracks = json.loads(Path('project.json').read_text())
  client = NotionClient(token_v2=settings.NOTION_TOKEN)

  root = client.get_block(settings.LYRICS_ROOT)

  for track in tracks:
    print(track['index'])
    print(track['title'])
    print(track['path'])
    child = root.children.add_new(PageBlock, title=track['title'])

    meta = challenge.get_track_meta(Path(track['path']))
    lyrics = meta.get('lyrics', '').split('\r')

    for line in lyrics:
      child.children.add_new(TextBlock, title=line)
      print(line)

    time.sleep(15)
