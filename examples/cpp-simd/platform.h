#ifndef PLATFORM_H
#define PLATFORM_H

// Architecture detection
#ifdef __x86_64__
    #define ARCH_X86_64 1
    #define SIMD_SUPPORT_SSE 1
    #define SIMD_SUPPORT_AVX 1
#elif defined(__i386__)
    #define ARCH_X86_32 1
    #define SIMD_SUPPORT_SSE 1
#elif defined(__aarch64__)
    #define ARCH_ARM64 1
    #define SIMD_SUPPORT_NEON 1
#elif defined(__arm__)
    #define ARCH_ARM32 1
    #define SIMD_SUPPORT_NEON 1
#else
    #define ARCH_UNKNOWN 1
#endif

// Compiler detection
#ifdef _MSC_VER
    #define COMPILER_MSVC 1
#elif defined(__GNUC__)
    #define COMPILER_GCC 1
#elif defined(__clang__)
    #define COMPILER_CLANG 1
#endif

// Platform-specific includes
#ifdef SIMD_SUPPORT_SSE
    #include <xmmintrin.h>  // SSE
    #include <emmintrin.h>  // SSE2
    #include <pmmintrin.h>  // SSE3
    #include <immintrin.h>  // AVX
#endif

#ifdef SIMD_SUPPORT_NEON
    #include <arm_neon.h>
#endif

// Memory alignment
#ifdef COMPILER_MSVC
    #define ALIGNED(x) __declspec(align(x))
#else
    #define ALIGNED(x) __attribute__((aligned(x)))
#endif

// Force inline
#ifdef COMPILER_MSVC
    #define FORCE_INLINE __forceinline
#else
    #define FORCE_INLINE __attribute__((always_inline)) inline
#endif

#endif // PLATFORM_H
