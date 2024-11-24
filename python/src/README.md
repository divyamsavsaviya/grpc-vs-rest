# GRPC threading Loop example

This lab/example uses Cmake to build a grpc server to test python to C++ integration as a
client-server relationship.

## Python Client

### Required packages

You will need to install (upgrade) the following packages:

   * python3 -m pip install --upgrade pip
   * python3 -m pip install grpcio
   * python3 -m pip install grpcio-tools

### Building 


```
mkdir py
cd py
python3 -m grpc_tools.protoc -I../resources --python_out=. --pyi_out=. --grpc_python_out=. ../resources/loop.proto
```


## C++ Client and Server

### C++ Required packages

   * Using brew, yum, or apt install grpc
   * download the source code for gRPC from github, we are after the 
     Module and examples directory
   * cmake

The **examples directory** contains a great resource on how to build 
features of gRPC across multiple languages. 

The **modules directory** provides the rules for discovering packages and 
provides a learning point to understand how to write your own custom 
finder.

### Building

For platform/OS specific requirements refer below. Otherwise, using CMake:

```
mkdir b
cd b
cmake ..
make
```

The call to `cmake ..` will generate the files from the `.proto` file in
the command `add_custom_command`. You can also run the command using 
(build-proto.sh):

```
#!/bin/sh

# source code directory - we need an absolute path to the .protoc otherwise,
# the generated files are nested in generated-src with the relative path.
base="/Users/gash/workspace-cpp/grpc/loop-grpc"

protoc --cpp_out ${base}/b/generated-src --grpc_out ${base}/b/generated-src \
       -I ${base}/resources \
       --plugin=protoc-gen-grpc=/opt/homebrew/Cellar/grpc/1.66.2/bin/grpc_cpp_plugin \
       ${base}/resources/loop.proto
```

### Windows Building

Visual Studio is your best bet here. VS already includes openmp.


### MAC OSX Building

If you have used brew to install your C++ compiler, grpc, protobuf, 
and possibily built other packages using gcc-x (GNUs not XCode) then
there is a likelihood that you are mixing libraries built with 
XCode (brew) and GNU.

This mixing is bad because of name mangling between LLVM and GNU. Errors
during linking is a sign that you are mixing.

What to do:

 * Instruct brew to use GNU (or clang) only - CXX and CC environment variables
 * Build from source - this includes all dependencies
 * Build with XCode (see below) 


### Building w/ XCode (likely the easiest)

 * You will need ensure that you used brew to install grpc, libomp, and protobuf
 * For openmp (libomp): brew install libomp

### Linux

 * Use apt-git, yum, or rpm whichever is your package installer for the distro.

### Credit/References/Reading

 * https://grpc.io/docs/quickstart/python.html
 * https://grpc.io/docs/what-is-grpc/faq/
 * https://cmake.org/cmake/help/latest/command/add_custom_command.html
 * https://github.com/IvanSafonov/grpc-cmake-example
 * https://iscinumpy.gitlab.io/post/omp-on-high-sierra
