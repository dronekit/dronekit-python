#!/bin/bash

cd $(dirname $0)
cd ..

DESTDIR=dronekit/lib
protoc --python_out=$DESTDIR --proto_path=../dronekit-protobuf/src ../dronekit-protobuf/src/webapi.proto
