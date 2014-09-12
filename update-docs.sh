#!/bin/bash

rm -r /tmp/autodocs
set -e
python ./setup.py build
echo Switching to doc tree
cd docs
make html
cp -a _build/html /tmp/autodocs
cd ..
git checkout gh-pages
cp -a /tmp/autodocs/* .
set +e
find . | xargs git add
set -e
git commit -m "Update docs"
git push
git checkout -f master

