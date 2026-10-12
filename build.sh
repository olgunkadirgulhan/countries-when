#!/bin/sh
# balls.py = src/ parçalarının birleşimi (yardımcılar ve ses Bloop Bonkers motorundan). Düzenleme src/ içinde yapılır.
cd "$(dirname "$0")" && cat src/head.py src/helpers.py src/bank.py src/scene.py > balls.py && echo "" >> balls.py && cat src/audio.py src/tail.py >> balls.py
