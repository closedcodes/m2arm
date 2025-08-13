# C++ SIMD Example

This example demonstrates a C++ project that uses x86 SIMD intrinsics and needs migration to ARM NEON.

## Files

- `math_utils.cpp` - Contains x86 SSE/AVX intrinsics that need ARM NEON equivalents
- `platform.h` - Contains architecture-specific preprocessor directives
- `CMakeLists.txt` - Build configuration that needs ARM support
- `README.md` - This file

## Current Status

The code currently uses x86-specific SIMD instructions:
- SSE intrinsics (`_mm_add_ps`, `_mm_mul_ps`, etc.)
- AVX intrinsics (`_mm256_add_ps`, etc.)
- Architecture checks (`#ifdef __x86_64__`)

## Migration Plan

1. Replace x86 intrinsics with ARM NEON equivalents
2. Add ARM architecture checks
3. Update CMake for cross-compilation
4. Test on ARM platforms

## Usage

```bash
# Scan for issues
m2arm scan .

# Create migration plan
m2arm plan --target arm64

# Apply migration (dry run first)
m2arm migrate --dry-run
m2arm migrate --apply

# Cross-compile
m2arm compile --targets linux/arm64,linux/amd64

# Test
m2arm test --platform arm64
```
