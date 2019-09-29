import csv
import subprocess
from pathlib import Path

from notion.client import NotionClient

import settings


def generate_lyrics_csv_file(url):
  if url is None:
    title = 'Fill name'
    text = subprocess.check_output(['pbpaste']).decode('utf-8').strip()
  else:
    client = NotionClient(token_v2=settings.NOTION_TOKEN)

    page = client.get_block(url)

    title = page.title
    text = '\n'.join(child.title for child in page.children)

  parts = text.split('===')
  text = parts[1].strip() if len(parts) > 1 else parts[0]

  print(text)

  output_file = Path(title + '.csv')

  with output_file.open('w') as fp:
    writer = csv.writer(fp)
    writer.writerow(['Chinese', 'English', 'Annotation'])
    for line in text.splitlines():
      if line == '':
        line = '_'

      writer.writerow([line, '', ''])

  print(f'Generated {output_file}')
