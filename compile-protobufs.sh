DESTDIR=droneapi/lib
protoc --python_out=$DESTDIR --proto_path=../droneapi-protobuf/src ../droneapi-protobuf/src/webapi.proto
