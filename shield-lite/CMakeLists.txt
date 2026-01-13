cmake_minimum_required(VERSION 3.15)
project(shield_lite_cpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Source files
set(SOURCES
    src/shield_lite/cpp/monte_carlo.cpp
    src/shield_lite/cpp/photon_transport.cpp
    src/shield_lite/cpp/bindings.cpp
)

# Create Python module
pybind11_add_module(_monte_carlo ${SOURCES})

# Enable optimization
target_compile_options(_monte_carlo PRIVATE
    $<$<CONFIG:Release>:-O3 -march=native>
)

# Installation
install(TARGETS _monte_carlo DESTINATION shield_lite)
