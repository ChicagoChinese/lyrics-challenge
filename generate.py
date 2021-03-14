import re
import csv
import json
import subprocess
from pathlib import Path

from notion.client import NotionClient

import settings


def generate_lyrics_csv_file_from_text():
    # input_file = Path(input_file)
    # text = input_file.read_text()
    title = input("Title: ")
    text = subprocess.check_output('pbpaste').decode()

    parts = re.split(r'={3,}', text)
    text = parts[1].strip() if len(parts) > 1 else parts[0]

    print(text)

    output_file = Path(title + '.csv')

    with output_file.open('w') as fp:
        writer = csv.writer(fp)
        writer.writerow(['English', 'Chinese', 'Annotation'])
        for line in text.splitlines():
            if line.strip() == '':
                line = '_'

            writer.writerow([line, '', ''])

    print(f'\nGenerated {output_file}')


def generate_lyrics_csv_file(url):
    client = NotionClient(token_v2=settings.NOTION_TOKEN)

    page = client.get_block(url)

    title = page.title
    text = '\n'.join(child.title for child in page.children)

    parts = re.split(r'={3,}', text)
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


def generate_lyrics_json_file(url):
    """
    Unfortunately, Notion, does not know how to import JSON files

    """
    client = NotionClient(token_v2=settings.NOTION_TOKEN)

    page = client.get_block(url)

    title = page.title
    text = '\n'.join(child.title for child in page.children)

    meta, body = re.split(r'={3,}', text)
    meta = meta.strip()
    body = body.strip()

    print(text)

    output_file = Path(title + '.json')

    with output_file.open('w') as fp:
        output = {'meta': meta, 'lines': body.splitlines()}
        json.dump(output, fp, ensure_ascii=False, indent=2)

    print(f'Generated {output_file}')
