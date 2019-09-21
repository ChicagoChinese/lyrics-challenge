import json
import itunes


if __name__ == '__main__':
  app = itunes.ITunes()
  plist = app['Grand Lyrics Project']

  objs = [{'path': str(track.path), 'title': track.title, 'index': i}
    for (i, track) in enumerate(plist.tracks, 1)]

  with open('project.json', 'w', encoding='utf-8') as fp:
    json.dump(objs, fp, ensure_ascii=False, indent=2)

