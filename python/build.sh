#!/bin/sh

# your protoc must match version numbers
PROTOC=/opt/homebrew/bin/protoc

# output generated code to
GENOUT=./looper

if [ ! -d $GENOUT ]; then
  mkdir $GENOUT
  touch ${GENOUT}/__init__.py
fi

cp ./src/loop_client.py $GENOUT/.

cd looper

python3 -m grpc_tools.protoc -I../../resources --python_out=. --pyi_out=. \
        --grpc_python_out=. ../../resources/loop.proto
