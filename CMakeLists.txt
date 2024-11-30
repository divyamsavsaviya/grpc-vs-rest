# Specify the minimum CMake version required
cmake_minimum_required(VERSION 3.13)

# Define project name and enable languages
project(grpc_performance_test CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add debugging flags for development
add_compile_options(-g)

# Set optimization level for release builds
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

# Enable extra warnings
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

# -----------------------------------------------------------------------
# Find required packages
# -----------------------------------------------------------------------

# Find OpenMP for parallel processing
find_package(OpenMP REQUIRED)

# Enable compatibility with Protobuf module
option(protobuf_MODULE_COMPATIBLE TRUE)

# Find Protobuf package
find_package(Protobuf CONFIG REQUIRED)
message(STATUS "Using protobuf ${Protobuf_VERSION}")

# Set Protobuf variables
set(_PROTOBUF_LIBPROTOBUF protobuf::libprotobuf)
if(CMAKE_CROSSCOMPILING)
    find_program(_PROTOBUF_PROTOC protoc)
else()
    set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc>)
endif()

# Find gRPC package
find_package(gRPC CONFIG REQUIRED)
message(STATUS "Using gRPC ${gRPC_VERSION}")

# Set gRPC variables
set(_GRPC_GRPCPP gRPC::grpc++)
if(CMAKE_CROSSCOMPILING)
    find_program(_GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
else()
    set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:gRPC::grpc_cpp_plugin>)
endif()

# find_path(HTTPLIB_INCLUDE_DIR httplib.h
#     PATHS /usr/local/include /usr/include
#     PATH_SUFFIXES httplib cpp-httplib
# )

include_directories(
    /opt/homebrew/include             # For general includes
    /opt/homebrew/Cellar/cpp-httplib/0.18.1/include 
    /mnt/d/grpc-vs-rest/include
)

# -----------------------------------------------------------------------
# Define Paths for Proto Files and Generated Code
# -----------------------------------------------------------------------

# Base directories for proto files
set(PROTO_BASE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/resources)

# Define paths for hello world proto
set(HELLO_WORLD_PROTO "${PROTO_BASE_DIR}/helloworld.proto")
set(HELLO_WORLD_PROTO_DIR ${CMAKE_CURRENT_BINARY_DIR}/generated-src/helloworld)

# Define paths for performance test proto
set(PERF_TEST_PROTO "${PROTO_BASE_DIR}/performance_test.proto")
set(PERF_TEST_PROTO_DIR ${CMAKE_CURRENT_BINARY_DIR}/generated-src/perftest)

# Create directories for generated files
file(MAKE_DIRECTORY ${HELLO_WORLD_PROTO_DIR})
file(MAKE_DIRECTORY ${PERF_TEST_PROTO_DIR})

# Add generated directories to include path
include_directories(
    ${CMAKE_CURRENT_BINARY_DIR}
    ${HELLO_WORLD_PROTO_DIR}
    ${PERF_TEST_PROTO_DIR}
)

# -----------------------------------------------------------------------
# Generate Code from Proto Files
# -----------------------------------------------------------------------

# Generate code for hello world proto
add_custom_command(
    OUTPUT
        "${HELLO_WORLD_PROTO_DIR}/helloworld.pb.cc"
        "${HELLO_WORLD_PROTO_DIR}/helloworld.pb.h"
        "${HELLO_WORLD_PROTO_DIR}/helloworld.grpc.pb.cc"
        "${HELLO_WORLD_PROTO_DIR}/helloworld.grpc.pb.h"
    COMMAND ${_PROTOBUF_PROTOC}
    ARGS --grpc_out "${HELLO_WORLD_PROTO_DIR}"
         --cpp_out "${HELLO_WORLD_PROTO_DIR}"
         -I "${PROTO_BASE_DIR}"
         --plugin=protoc-gen-grpc=${_GRPC_CPP_PLUGIN_EXECUTABLE}
         "${HELLO_WORLD_PROTO}"
    DEPENDS "${HELLO_WORLD_PROTO}"
)

# Generate code for performance test proto
add_custom_command(
    OUTPUT
        "${PERF_TEST_PROTO_DIR}/performance_test.pb.cc"
        "${PERF_TEST_PROTO_DIR}/performance_test.pb.h"
        "${PERF_TEST_PROTO_DIR}/performance_test.grpc.pb.cc"
        "${PERF_TEST_PROTO_DIR}/performance_test.grpc.pb.h"
    COMMAND ${_PROTOBUF_PROTOC}
    ARGS --grpc_out "${PERF_TEST_PROTO_DIR}"
         --cpp_out "${PERF_TEST_PROTO_DIR}"
         -I "${PROTO_BASE_DIR}"
         --plugin=protoc-gen-grpc=${_GRPC_CPP_PLUGIN_EXECUTABLE}
         "${PERF_TEST_PROTO}"
    DEPENDS "${PERF_TEST_PROTO}"
)

# -----------------------------------------------------------------------
# Define Source Files
# -----------------------------------------------------------------------

set(SERVER_SOURCES
    src/helloworldImpl.cc
    ${HELLO_WORLD_PROTO_DIR}/helloworld.pb.cc
    ${HELLO_WORLD_PROTO_DIR}/helloworld.grpc.pb.cc
    ${PERF_TEST_PROTO_DIR}/performance_test.pb.cc
    ${PERF_TEST_PROTO_DIR}/performance_test.grpc.pb.cc
)

# -----------------------------------------------------------------------
# Define Executables
# -----------------------------------------------------------------------

# Add the server executable
add_executable(helloworld-server ${SERVER_SOURCES})
# Rest server executable
add_executable(rest-server 
    src/rest_server.cpp
)


# -----------------------------------------------------------------------
# Link Libraries
# -----------------------------------------------------------------------

target_link_libraries(helloworld-server
    PRIVATE
        ${_GRPC_GRPCPP}
        ${_PROTOBUF_LIBPROTOBUF}
        gRPC::grpc++_reflection
        OpenMP::OpenMP_CXX
)

# -----------------------------------------------------------------------
# Set Target Properties
# -----------------------------------------------------------------------

# Set properties for the server executable
set_target_properties(helloworld-server
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

# Add compile definitions for different build types
target_compile_definitions(helloworld-server
    PRIVATE
    $<$<CONFIG:Debug>:DEBUG>
    $<$<CONFIG:Release>:NDEBUG>
)

# Set optimization flags for Release build
target_compile_options(helloworld-server
    PRIVATE
    $<$<CONFIG:Release>:-O3 -march=native>
    $<$<CONFIG:Debug>:-O0 -g>
)

# target_include_directories(rest-server 
#     PRIVATE 
#     ${HTTPLIB_INCLUDE_DIR}
# )

target_link_libraries(rest-server
    PRIVATE
    OpenMP::OpenMP_CXX
)

# -----------------------------------------------------------------------
# Installation Rules (Optional)
# -----------------------------------------------------------------------

install(TARGETS helloworld-server
    RUNTIME DESTINATION bin
)

# -----------------------------------------------------------------------
# Print Configuration Summary
# -----------------------------------------------------------------------

message(STATUS "Configuration Summary")
message(STATUS "-------------------")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "C++ Flags: ${CMAKE_CXX_FLAGS}")
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    message(STATUS "Release flags: ${CMAKE_CXX_FLAGS_RELEASE}")
elseif(CMAKE_BUILD_TYPE STREQUAL "Debug")
    message(STATUS "Debug flags: ${CMAKE_CXX_FLAGS_DEBUG}")
endif()