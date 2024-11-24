#!/bin/sh
#
# This is an example to manually create the protobuf and grpc source files. 
#

# source code directory - we need an absolute path to the .protoc otherwise,
# the generated files are nested in generated-src with the relative path.
base="/Users/gash/workspace-cpp/grpc/loop-grpc"

protoc --cpp_out ${base}/b/generated-src --grpc_out ${base}/b/generated-src \
       -I ${base}/resources \
       --plugin=protoc-gen-grpc=/opt/homebrew/Cellar/grpc/1.66.2/bin/grpc_cpp_plugin \
       ${base}/resources/loop.proto

