from settings import NOTION_API_TOKEN
from notion_client import Client

notion = Client(auth=NOTION_API_TOKEN)
result = notion.search(query='月亮小姐')
for o in result['results']:
  print(o['object'], o['id'])

# Doesn't return anything
print(notion.search(query='林孟璇'))

page = notion.pages.retrieve(page_id='8d422f94-c904-4113-a683-197ff00aef20')

db = notion.databases.retrieve(database_id='df4dfb3f-f36f-462d-ad6e-1ef29f1867eb')
result = notion.databases.query(
  database_id='df4dfb3f-f36f-462d-ad6e-1ef29f1867eb',
  sorts=[{'direction': 'ascending', 'timestamp': 'created_time'}])
for row in result['results']:
  title = row['properties']['Chinese']['title']
  if len(title) == 0:
    print('')
  else:
    print(title[0]['plain_text'])

# Doesn't work for database IDs
result = notion.blocks.children.list(block_id='df4dfb3f-f36f-462d-ad6e-1ef29f1867eb')
