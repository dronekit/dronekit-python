#!/bin/bash

cd $(dirname $0)
cd ..

sudo python setup.py sdist bdist_egg bdist_wheel upload
