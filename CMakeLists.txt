# Specify the minimum CMake version required for this project
cmake_minimum_required(VERSION 3.3)

# Define the name of the project
project(grpcvsrest)

# Set the C++ standard to C++17 for modern C++ features
set(CMAKE_CXX_STANDARD 17)

# Add debugging flags for development (-g for debug information)
add_compile_options(-g)

# Set optimization level for release builds (-O3 for maximum optimization)
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

# -----------------------------------------------------------------------
# Compiler Setup (Optional)
# Uncomment and modify the lines below if you need to specify custom compilers
# for your project, like a specific version of GCC or Clang.
#
# Example:
# set(CMAKE_C_COMPILER /usr/local/bin/gcc-13)
# set(CMAKE_CXX_COMPILER /usr/local/bin/g++-13)
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------
# OpenMP Setup for Threading
# This enables parallel programming features using OpenMP.
find_package(OpenMP REQUIRED)

# -----------------------------------------------------------------------
# Protobuf and gRPC Setup
# This section configures Protobuf and gRPC dependencies.
# -----------------------------------------------------------------------

# Enable compatibility with Protobuf module
option(protobuf_MODULE_COMPATIBLE TRUE)

# Find Protobuf library and log the version being used
find_package(Protobuf CONFIG REQUIRED)
message(STATUS "Using protobuf ${Protobuf_VERSION}")

# Set Protobuf-related variables for linking and protoc (Protobuf compiler)
set(_PROTOBUF_LIBPROTOBUF protobuf::libprotobuf)
if(CMAKE_CROSSCOMPILING)
    find_program(_PROTOBUF_PROTOC protoc) # Cross-compiling requires specifying the path to protoc
else()
    set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc>) # Use default Protobuf compiler
endif()

# Find gRPC library and log the version being used
find_package(gRPC CONFIG REQUIRED)
message(STATUS "Using gRPC ${gRPC_VERSION}")

# Set gRPC-related variables for linking and the gRPC plugin
set(_GRPC_GRPCPP gRPC::grpc++)
if(CMAKE_CROSSCOMPILING)
    find_program(_GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin) # Cross-compiling requires path to gRPC plugin
else()
    set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:gRPC::grpc_cpp_plugin>) # Use default plugin
endif()

# -----------------------------------------------------------------------
# Define Paths for .proto Files and Generated Code
# This section specifies where to find .proto files and where to place
# the generated C++ source and header files.
# -----------------------------------------------------------------------

# Base directory containing .proto files
set(PROTOS_BASE ${CMAKE_CURRENT_SOURCE_DIR}/resources)

# Define paths for the new proto
set(HELLO_WORLD_PROTO_BASE ${CMAKE_CURRENT_SOURCE_DIR}/resources)
set(HELLO_WORLD_PROTO ${HELLO_WORLD_PROTO_BASE}/helloworld.proto)

set(HELLO_WORLD_PROTO_SRC_DIR ${CMAKE_CURRENT_BINARY_DIR}/generated-src/helloworld)
file(MAKE_DIRECTORY ${HELLO_WORLD_PROTO_SRC_DIR})
include_directories(${HELLO_WORLD_PROTO_SRC_DIR})

# Paths for generated code
set(HELLO_WORLD_PROTO_SRCS "${HELLO_WORLD_PROTO_SRC_DIR}/helloworld.pb.cc")
set(HELLO_WORLD_GRPC_SRCS "${HELLO_WORLD_PROTO_SRC_DIR}/helloworld.grpc.pb.cc")
set(HELLO_WORLD_PROTO_HDRS "${HELLO_WORLD_PROTO_SRC_DIR}/helloworld.pb.h")
set(HELLO_WORLD_GRPC_HDRS "${HELLO_WORLD_PROTO_SRC_DIR}/helloworld.grpc.pb.h")

# Custom command for generating protobuf and gRPC files for helloworld.proto
add_custom_command(
   OUTPUT "${HELLO_WORLD_PROTO_SRCS}" "${HELLO_WORLD_GRPC_SRCS}" "${HELLO_WORLD_PROTO_HDRS}" "${HELLO_WORLD_GRPC_HDRS}"
   COMMAND ${_PROTOBUF_PROTOC}
   ARGS --grpc_out "${HELLO_WORLD_PROTO_SRC_DIR}"
        --cpp_out "${HELLO_WORLD_PROTO_SRC_DIR}"
        -I "${HELLO_WORLD_PROTO_BASE}"
        --plugin=protoc-gen-grpc=${_GRPC_CPP_PLUGIN_EXECUTABLE}
        "${HELLO_WORLD_PROTO}"
   DEPENDS "${HELLO_WORLD_PROTO}"
   COMMENT "Creating generated protobuf/grpc files for helloworld.proto"
   VERBATIM
)

# Include the directory containing the generated code
include_directories("${HELLO_WORLD_PROTO_SRC_DIR}")

# Define a new server executable for helloworld.proto
add_executable(helloworld-server 
   src/helloworldImpl.cc 
   ${HELLO_WORLD_PROTO_SRCS} 
   ${HELLO_WORLD_GRPC_SRCS}
)

# Link the libraries for the helloworld server
target_link_libraries(helloworld-server
   gRPC::grpc++_reflection
   protobuf::libprotobuf
)
