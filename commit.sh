#!/bin/bash

#sleep "$1" && xmms /home/demo/.local/share/myscripts/alerm.mp3
#sleep "$1" && mpv /home/demo/.local/share/myscripts/alerm.mp3
#sleep $1 
git config user.name github-actions[bot]
git config user.email 41898282+github-actions[bot]@users.noreply.github.com
git add .
git commit --author=. -m 'manual modify'
git push

exit 0

#sleep "$1" && celluloid /home/demo/.local/share/myscripts/alerm.mp3

