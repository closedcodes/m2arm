#include "platform.h"
#include <vector>
#include <cstring>

// Vector addition using x86 SIMD intrinsics
void add_vectors_x86(const float* a, const float* b, float* result, size_t length) {
#ifdef SIMD_SUPPORT_SSE
    size_t simd_length = length & ~3; // Round down to multiple of 4
    
    for (size_t i = 0; i < simd_length; i += 4) {
        __m128 va = _mm_load_ps(&a[i]);
        __m128 vb = _mm_load_ps(&b[i]);
        __m128 vr = _mm_add_ps(va, vb);
        _mm_store_ps(&result[i], vr);
    }
    
    // Handle remaining elements
    for (size_t i = simd_length; i < length; ++i) {
        result[i] = a[i] + b[i];
    }
#else
    // Fallback to scalar
    for (size_t i = 0; i < length; ++i) {
        result[i] = a[i] + b[i];
    }
#endif
}

// Vector multiplication using x86 SIMD intrinsics
void multiply_vectors_x86(const float* a, const float* b, float* result, size_t length) {
#ifdef SIMD_SUPPORT_SSE
    size_t simd_length = length & ~3;
    
    for (size_t i = 0; i < simd_length; i += 4) {
        __m128 va = _mm_load_ps(&a[i]);
        __m128 vb = _mm_load_ps(&b[i]);
        __m128 vr = _mm_mul_ps(va, vb);
        _mm_store_ps(&result[i], vr);
    }
    
    for (size_t i = simd_length; i < length; ++i) {
        result[i] = a[i] * b[i];
    }
#else
    for (size_t i = 0; i < length; ++i) {
        result[i] = a[i] * b[i];
    }
#endif
}

// Dot product using x86 SIMD intrinsics
float dot_product_x86(const float* a, const float* b, size_t length) {
#ifdef SIMD_SUPPORT_SSE
    __m128 sum = _mm_setzero_ps();
    size_t simd_length = length & ~3;
    
    for (size_t i = 0; i < simd_length; i += 4) {
        __m128 va = _mm_load_ps(&a[i]);
        __m128 vb = _mm_load_ps(&b[i]);
        __m128 prod = _mm_mul_ps(va, vb);
        sum = _mm_add_ps(sum, prod);
    }
    
    // Horizontal sum of the vector
    ALIGNED(16) float temp[4];
    _mm_store_ps(temp, sum);
    float result = temp[0] + temp[1] + temp[2] + temp[3];
    
    // Handle remaining elements
    for (size_t i = simd_length; i < length; ++i) {
        result += a[i] * b[i];
    }
    
    return result;
#else
    float result = 0.0f;
    for (size_t i = 0; i < length; ++i) {
        result += a[i] * b[i];
    }
    return result;
#endif
}

// Matrix multiplication using x86 SIMD (simplified 4x4)
void matrix_multiply_4x4_x86(const float* a, const float* b, float* result) {
#ifdef SIMD_SUPPORT_SSE
    for (int i = 0; i < 4; ++i) {
        __m128 row = _mm_load_ps(&a[i * 4]);
        
        for (int j = 0; j < 4; ++j) {
            __m128 col = _mm_set_ps(b[12 + j], b[8 + j], b[4 + j], b[j]);
            __m128 prod = _mm_mul_ps(row, col);
            
            // Horizontal sum
            __m128 sum1 = _mm_hadd_ps(prod, prod);
            __m128 sum2 = _mm_hadd_ps(sum1, sum1);
            _mm_store_ss(&result[i * 4 + j], sum2);
        }
    }
#else
    // Fallback scalar implementation
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 4; ++j) {
            float sum = 0.0f;
            for (int k = 0; k < 4; ++k) {
                sum += a[i * 4 + k] * b[k * 4 + j];
            }
            result[i * 4 + j] = sum;
        }
    }
#endif
}

// Memory copy with x86 optimizations
void fast_memcpy_x86(void* dest, const void* src, size_t size) {
#ifdef SIMD_SUPPORT_SSE
    const char* src_ptr = static_cast<const char*>(src);
    char* dest_ptr = static_cast<char*>(dest);
    
    size_t simd_size = size & ~15; // Round down to multiple of 16
    
    for (size_t i = 0; i < simd_size; i += 16) {
        __m128i data = _mm_loadu_si128(reinterpret_cast<const __m128i*>(&src_ptr[i]));
        _mm_storeu_si128(reinterpret_cast<__m128i*>(&dest_ptr[i]), data);
    }
    
    // Handle remaining bytes
    std::memcpy(&dest_ptr[simd_size], &src_ptr[simd_size], size - simd_size);
#else
    std::memcpy(dest, src, size);
#endif
}

// Example usage function
int main() {
    constexpr size_t length = 1024;
    std::vector<float> a(length, 1.0f);
    std::vector<float> b(length, 2.0f);
    std::vector<float> result(length);
    
    // Test vector operations
    add_vectors_x86(a.data(), b.data(), result.data(), length);
    multiply_vectors_x86(a.data(), b.data(), result.data(), length);
    
    float dot = dot_product_x86(a.data(), b.data(), length);
    
    // Test matrix multiplication
    std::vector<float> matrix_a(16, 1.0f);
    std::vector<float> matrix_b(16, 2.0f);
    std::vector<float> matrix_result(16);
    
    matrix_multiply_4x4_x86(matrix_a.data(), matrix_b.data(), matrix_result.data());
    
    return 0;
}
