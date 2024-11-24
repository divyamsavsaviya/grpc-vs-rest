# Specify the minimum CMake version required for this project
cmake_minimum_required(VERSION 3.3)

# Define the name of the project
project(loop)

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

# List of .proto files to process
set(PROTOS ${PROTOS_BASE}/loop.proto)

# Directory to store generated source and header files
set(PROTO_SRC_DIR ${CMAKE_CURRENT_BINARY_DIR}/generated-src)
file(MAKE_DIRECTORY ${PROTO_SRC_DIR})

# Include the directory for generated files in the project
include_directories(${PROTO_SRC_DIR})

# Define the expected output files for the .proto file
set(PROTO_SRCS "${PROTO_SRC_DIR}/loop.pb.cc")
set(GRPC_SRCS "${PROTO_SRC_DIR}/loop.grpc.pb.cc")
set(PROTO_HDRS "${PROTO_SRC_DIR}/loop.pb.h")
set(GRPC_HDRS "${PROTO_SRC_DIR}/loop.grpc.pb.h")

# Log the gRPC plugin path for debugging purposes
message(STATUS "grpc plugin: ${_GRPC_CPP_PLUGIN_EXECUTABLE}")

# -----------------------------------------------------------------------
# Custom Command to Generate Protobuf and gRPC Files
# This will regenerate the C++ bindings whenever the .proto file changes.
# -----------------------------------------------------------------------

add_custom_command(
    OUTPUT "${PROTO_SRCS}" "${GRPC_SRCS}" "${PROTO_HDRS}" "${GRPC_HDRS}"
    COMMAND ${_PROTOBUF_PROTOC}
    ARGS --grpc_out "${PROTO_SRC_DIR}" # Generate gRPC bindings
         --cpp_out "${PROTO_SRC_DIR}"  # Generate Protobuf bindings
         -I "${PROTOS_BASE}"           # Include directory for .proto files
         --plugin=protoc-gen-grpc=${_GRPC_CPP_PLUGIN_EXECUTABLE} # Specify gRPC plugin
         "${PROTOS}"                   # Input .proto file
    DEPENDS "${PROTOS}"                # Rebuild if .proto file changes
    COMMENT "Creating generated protobuf/gRPC files"
    VERBATIM
)

# Add the directory with generated files to the include paths
include_directories(${PROTO_SRC_DIR})

# -----------------------------------------------------------------------
# Build Targets (Executables and Libraries)
# -----------------------------------------------------------------------

# Main executable for a standalone program
add_executable(loop-main
    src/looping.cc
)

# Server binary with threading support (OpenMP)
add_executable(loop-server 
    src/loopImpl.cc 
    ${PROTO_SRCS} 
    ${GRPC_SRCS}
)

# Non-threaded server binary
add_executable(loop-nt-server 
    src/loopImpl.cc 
    ${PROTO_SRCS} 
    ${GRPC_SRCS}
)

# -----------------------------------------------------------------------
# Linking Libraries to Targets
# This section specifies which libraries are required for each binary.
# -----------------------------------------------------------------------

# Link the main executable with OpenMP for parallel processing
target_link_libraries(loop-main
    OpenMP::OpenMP_CXX
)

# Link the server binary with gRPC, Protobuf, and OpenMP
target_link_libraries(loop-server
    gRPC::grpc++_reflection  # gRPC reflection library
    protobuf::libprotobuf    # Protobuf library
    OpenMP::OpenMP_CXX       # OpenMP for threading
)

# Link the non-threaded server binary with gRPC and Protobuf
target_link_libraries(loop-nt-server
    gRPC::grpc++_reflection
    protobuf::libprotobuf
)

# -----------------------------------------------------------------------
# Notes for Modification:
# - To add new .proto files:
#   1. Add their paths to the `PROTOS` variable.
#   2. Ensure the new files are added to the custom command if needed.
#
# - To add new source files:
#   - Include them in the appropriate `add_executable` command.
#
# - To link additional libraries:
#   - Use `target_link_libraries` to specify the libraries for each target.
#
# - If you encounter path issues, check the variables `PROTO_SRC_DIR` and
#   `PROTOS_BASE` to ensure they point to the correct locations.
# -----------------------------------------------------------------------
