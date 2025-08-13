cmake_minimum_required(VERSION 3.16)
project(SIMDExample)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Architecture detection
if(CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "AMD64")
    set(ARCH_X86_64 ON)
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "i386" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "i686")
    set(ARCH_X86_32 ON)
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64")
    set(ARCH_ARM64 ON)
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "arm")
    set(ARCH_ARM32 ON)
endif()

# Compiler flags for x86
if(ARCH_X86_64 OR ARCH_X86_32)
    if(MSVC)
        target_compile_options(${PROJECT_NAME} PRIVATE /arch:SSE2 /arch:AVX)
    else()
        target_compile_options(${PROJECT_NAME} PRIVATE -msse -msse2 -msse3 -mavx)
    endif()
endif()

# Compiler flags for ARM (will need to be added for ARM migration)
if(ARCH_ARM64 OR ARCH_ARM32)
    if(NOT MSVC)
        target_compile_options(${PROJECT_NAME} PRIVATE -march=armv8-a -mtune=cortex-a72)
    endif()
endif()

# Source files
set(SOURCES
    math_utils.cpp
    platform.h
)

# Create executable
add_executable(${PROJECT_NAME} ${SOURCES})

# Platform-specific libraries
if(WIN32)
    # Windows-specific libraries
elseif(UNIX)
    # Unix-specific libraries
    find_package(Threads REQUIRED)
    target_link_libraries(${PROJECT_NAME} Threads::Threads)
endif()

# Optimization flags
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    if(MSVC)
        target_compile_options(${PROJECT_NAME} PRIVATE /O2 /Ob2)
    else()
        target_compile_options(${PROJECT_NAME} PRIVATE -O3 -ffast-math -funroll-loops)
    endif()
endif()

# Install targets
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
)
