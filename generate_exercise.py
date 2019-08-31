import sys
import subprocess
from pathlib import Path

import settings


music_dir = Path(settings.MUSIC_DIR)


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
    print(f'Processing {track}')


if __name__ == '__main__':
  main()
