import csv
from pathlib import Path

from notion.client import NotionClient

import settings


def generate_lyrics_csv_file(url):
  client = NotionClient(token_v2=settings.NOTION_TOKEN)

  page = client.get_block(url)

  print(page.title)

  output_file = Path(page.title + '.csv')

  with output_file.open('w') as fp:
    writer = csv.writer(fp)
    writer.writerow(['Chinese', 'English', 'Annotation'])
    for child in page.children:
      text = child.title
      if text == '':
        text = '_'

      writer.writerow([text, '', ''])

  print(f'Generated {output_file}')
