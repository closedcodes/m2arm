# M2ARM Documentation

Welcome to M2ARM - the comprehensive toolkit for migrating and modernizing applications from x86 to ARM architecture.

## Quick Start

### Installation

**Via Script (Recommended):**
```bash
curl -sSL https://get.m2arm.dev | bash
```

**Manual Installation:**
```bash
# Download latest release
wget https://github.com/m2arm/m2arm/releases/latest/download/m2arm-linux-amd64.tar.gz
tar -xzf m2arm-linux-amd64.tar.gz
sudo mv m2arm /usr/local/bin/
```

### Basic Usage

```bash
# 1. Scan your project
m2arm scan /path/to/your/project

# 2. Create migration plan
m2arm plan --target arm64

# 3. Execute migration (dry run first)
m2arm migrate --dry-run
m2arm migrate --apply

# 4. Cross-compile for ARM
m2arm compile --targets linux/arm64,windows/arm64

# 5. Test on ARM platforms
m2arm test --platform arm64
```

## Table of Contents

1. [Installation](#installation)
2. [Commands Reference](#commands-reference)
3. [Migration Workflow](#migration-workflow)
4. [Configuration](#configuration)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)
7. [SDK Reference](#sdk-reference)

## Commands Reference

### `m2arm scan`

Scan your codebase for x86-specific code and dependencies.

```bash
m2arm scan [path] [flags]
```

**Flags:**
- `-r, --recursive`: Recursively scan subdirectories (default: true)
- `--format`: Output format (table, json, summary) (default: table)
- `-v, --verbose`: Verbose output

**Examples:**
```bash
m2arm scan .                    # Scan current directory
m2arm scan /path/to/project     # Scan specific path
m2arm scan . --format json     # JSON output
m2arm scan . --format summary  # Summary only
```

### `m2arm plan`

Create a detailed migration plan based on scan results.

```bash
m2arm plan [path] [flags]
```

**Flags:**
- `-t, --target`: Target ARM architecture (arm64, armv7) (default: arm64)
- `--format`: Output format (text, json) (default: text)

**Examples:**
```bash
m2arm plan .                    # Create plan for current directory
m2arm plan --target arm64       # Target ARM64 specifically
m2arm plan . --format json     # JSON output
```

### `m2arm migrate`

Execute the migration plan to apply ARM-compatible changes.

```bash
m2arm migrate [path] [flags]
```

**Flags:**
- `--apply`: Apply changes (default is dry-run)
- `--dry-run`: Simulate migration without applying changes
- `--backup`: Create backup before applying changes (default: true)

**Examples:**
```bash
m2arm migrate --dry-run         # Simulate migration
m2arm migrate --apply           # Apply changes
m2arm migrate --apply --no-backup  # Apply without backup
```

### `m2arm compile`

Cross-compile your project for multiple architectures.

```bash
m2arm compile [flags]
```

**Flags:**
- `--targets`: Comma-separated list of targets
- `--output-dir`: Output directory for binaries

**Supported Targets:**
- `linux/amd64`, `linux/arm64`
- `windows/amd64`, `windows/arm64`
- `darwin/amd64`, `darwin/arm64`

**Examples:**
```bash
m2arm compile --targets linux/arm64,linux/amd64
m2arm compile --targets windows/arm64 --output-dir dist
```

### `m2arm test`

Test your ARM builds using emulation and containers.

```bash
m2arm test [flags]
```

**Flags:**
- `--platform`: Target platforms to test
- `--environment`: Test environment (native, emulated, container)

**Examples:**
```bash
m2arm test --platform arm64
m2arm test --platform arm64 --environment emulated
```

### `m2arm optimize`

Analyze and optimize performance for ARM architectures.

```bash
m2arm optimize [flags]
```

**Flags:**
- `--target`: Target ARM architecture
- `--profile`: Enable performance profiling

**Examples:**
```bash
m2arm optimize --target arm64
m2arm optimize --target arm64 --profile
```

## Migration Workflow

### 1. Assessment Phase

**Goal:** Understand the scope of migration required.

```bash
# Scan your project
m2arm scan .

# Review the scan results
# - Check for high-severity issues
# - Verify dependency compatibility
# - Note build system requirements
```

**Key Questions:**
- How many x86-specific instructions are used?
- Are dependencies ARM-compatible?
- What build systems need updating?

### 2. Planning Phase

**Goal:** Create a detailed migration strategy.

```bash
# Create migration plan
m2arm plan --target arm64

# Review the plan
# - Check migration steps
# - Verify confidence levels
# - Understand testing strategy
```

**Plan Components:**
- **Code Changes:** Specific file modifications
- **Build Updates:** Build system configurations
- **Dependencies:** Compatibility assessments
- **Testing:** Validation strategy

### 3. Migration Phase

**Goal:** Apply ARM-compatible changes to your code.

```bash
# Simulate migration first
m2arm migrate --dry-run

# Review planned changes
# - Verify replacements look correct
# - Check confidence levels
# - Note manual review items

# Apply migration
m2arm migrate --apply
```

**Best Practices:**
- Always run dry-run first
- Review high-confidence changes
- Manually verify low-confidence changes
- Keep backups of original code

### 4. Compilation Phase

**Goal:** Build your application for ARM targets.

```bash
# Cross-compile for multiple targets
m2arm compile --targets linux/arm64,linux/amd64,windows/arm64

# Check compilation results
# - Verify successful builds
# - Review any compilation errors
# - Test binary compatibility
```

**Target Selection:**
- Include both ARM and x86 for compatibility
- Choose appropriate target platforms
- Consider container deployment needs

### 5. Testing Phase

**Goal:** Validate ARM builds work correctly.

```bash
# Test on ARM platforms
m2arm test --platform arm64

# Run comprehensive tests
# - Unit tests
# - Integration tests
# - Performance tests
```

**Testing Environments:**
- **Native ARM:** Best performance, real hardware
- **Emulated ARM:** Available on x86, slower
- **Container:** Isolated, reproducible

### 6. Optimization Phase

**Goal:** Tune performance for ARM architecture.

```bash
# Analyze and optimize
m2arm optimize --target arm64

# Review optimization suggestions
# - ARM NEON opportunities
# - Compiler flag improvements
# - Memory access patterns
```

**Optimization Areas:**
- **SIMD:** ARM NEON intrinsics
- **Memory:** Cache-friendly access patterns
- **Compiler:** ARM-specific flags
- **Power:** ARM big.LITTLE scheduling

## Configuration

### Configuration File

M2ARM uses a YAML configuration file (`.m2arm.yaml`) for project-specific settings.

**Location Priority:**
1. Current directory (`./.m2arm.yaml`)
2. Home directory (`~/.m2arm.yaml`)
3. Command-line flags

**Example Configuration:**
```yaml
# Project settings
project:
  name: "my-project"
  languages: ["cpp", "python"]
  
# Scan settings
scan:
  recursive: true
  extensions: [".c", ".cpp", ".h", ".hpp", ".py"]
  skip_dirs: ["build", "dist", "node_modules"]
  
# Migration settings
migration:
  target_arch: "arm64"
  backup: true
  confidence_threshold: "medium"
  
# Compilation settings
compilation:
  default_targets: ["linux/arm64", "linux/amd64"]
  optimization_level: "O3"
  
# Testing settings
testing:
  default_platform: "arm64"
  timeout: 300
  
# Optimization settings
optimization:
  enable_neon: true
  memory_alignment: 64
```

### Environment Variables

M2ARM respects these environment variables:

- `M2ARM_CONFIG`: Path to configuration file
- `M2ARM_VERBOSE`: Enable verbose output
- `M2ARM_TARGET`: Default target architecture
- `M2ARM_OUTPUT`: Default output format

## Examples

### C++ Project with SIMD

```bash
# Navigate to C++ project
cd examples/cpp-simd

# Scan for x86 intrinsics
m2arm scan .

# Expected output:
# - x86 SSE/AVX intrinsics found
# - Architecture checks detected
# - CMake needs ARM support

# Create migration plan
m2arm plan --target arm64

# Apply migration
m2arm migrate --apply

# Cross-compile
m2arm compile --targets linux/arm64

# Test
m2arm test --platform arm64
```

### Python Project with Native Dependencies

```bash
# Scan Python project
m2arm scan .

# Check dependency compatibility
# Review requirements.txt ARM support

# No code migration needed for pure Python
# Focus on dependency verification

# Test with ARM Python
m2arm test --platform arm64
```

### Go Project

```bash
# Scan Go project
m2arm scan .

# Go has good ARM support
# Check for CGO dependencies

# Cross-compile easily
m2arm compile --targets linux/arm64,darwin/arm64

# Test binaries
m2arm test --platform arm64
```

## Troubleshooting

### Common Issues

**1. "No ARM toolchain found"**
```bash
# Install ARM cross-compilation tools
# Ubuntu/Debian:
sudo apt-get install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# RHEL/CentOS:
sudo yum install gcc-aarch64-linux-gnu

# macOS:
brew install aarch64-elf-gcc
```

**2. "Dependency not ARM compatible"**
```bash
# Check PyPI for ARM wheels
pip install --only-binary=all package_name

# For unavailable packages:
pip install --no-binary package_name  # Build from source
```

**3. "QEMU emulation not available"**
```bash
# Install QEMU for ARM emulation
# Ubuntu/Debian:
sudo apt-get install qemu-user-static

# Register binfmt for seamless execution
sudo systemctl start systemd-binfmt
```

**4. "Cross-compilation fails"**
```bash
# Check toolchain installation
aarch64-linux-gnu-gcc --version

# Verify build system configuration
# Update CMakeLists.txt or Makefile for ARM

# Set environment variables
export CC=aarch64-linux-gnu-gcc
export CXX=aarch64-linux-gnu-g++
```

### Performance Issues

**1. "ARM binary slower than x86"**
- Check if ARM NEON optimizations are enabled
- Verify compiler optimization flags (-O3)
- Profile with ARM-specific tools
- Consider ARM big.LITTLE scheduling

**2. "High memory usage on ARM"**
- Check data structure alignment
- Optimize for ARM cache hierarchy
- Use ARM-specific memory allocators

### Getting Help

**GitHub Issues:** https://github.com/m2arm/m2arm/issues
**Discussions:** https://github.com/m2arm/m2arm/discussions
**Email:** support@m2arm.dev

## SDK Reference

### Python SDK

The M2ARM Python SDK provides programmatic access to all functionality.

**Installation:**
```bash
pip install m2arm-sdk
```

**Basic Usage:**
```python
from m2arm import M2ARMCore

# Initialize
core = M2ARMCore("/path/to/project")

# Scan project
results = core.scan_project()

# Create migration plan
plan = core.create_migration_plan("arm64")

# Execute migration
core.execute_migration(plan, dry_run=True)

# Cross-compile
core.cross_compile(["linux/arm64", "linux/amd64"])

# Test
core.run_tests(["arm64"])

# Optimize
core.optimize_performance("arm64")
```

**Advanced Usage:**
```python
# Custom configuration
config = {
    "scan": {
        "extensions": [".c", ".cpp", ".h"],
        "skip_patterns": ["test_*", "*_backup"]
    },
    "migration": {
        "confidence_threshold": "high",
        "backup": True
    }
}

core = M2ARMCore("/path/to/project", config)

# Full workflow
results = core.full_migration_workflow(
    target_arch="arm64",
    compile_targets=["linux/arm64", "windows/arm64"]
)
```

### API Reference

For complete API documentation, see: [API Reference](https://docs.m2arm.dev/api/)

## Best Practices

### Code Organization

- Keep x86 and ARM code paths clearly separated
- Use conditional compilation for architecture-specific code
- Maintain portable fallbacks for unsupported platforms

### Testing Strategy

- Test on both emulated and native ARM hardware
- Include performance regression testing
- Validate across different ARM implementations

### Performance Optimization

- Profile before and after migration
- Focus on hot paths and SIMD opportunities
- Consider ARM-specific optimization techniques

### Deployment

- Build multi-architecture containers
- Use ARM-optimized base images
- Consider ARM-specific deployment strategies
