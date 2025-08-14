# M2ARM - Migration and Modernization to ARM

M2ARM is a comprehensive SDK and CLI toolkit designed to help developers migrate, modernize, and deploy applications across ARM and x86 architectures with minimal manual effort.

## 🎯 Purpose

- **Modernize**: Update legacy x86 software to be ARM-compatible and efficient
- **Migrate**: Help developers move their apps from x86 to ARM with minimal manual effort
- **Cross-Platform Support**: Ensure apps run on ARM (Raspberry Pi, Apple M1/M2, AWS Graviton) and x86 (PCs, servers)

## 🏗️ Architecture

### Python SDK
Core logic for:
- Code analysis and scanning
- Migration planning and execution
- Cross-compilation orchestration
- Testing and validation
- Performance optimization

### Go CLI
User-friendly command-line interface that:
- Provides intuitive commands for all SDK features
- Compiles to standalone binaries for multiple platforms
- Supports Windows, Linux, macOS on both ARM and x86

## ✨ Key Features

- 🔍 **Code Scanning**: Detect x86-specific instructions and platform dependencies
- 🔄 **Smart Migration**: Suggest and apply ARM-compatible alternatives (NEON instructions, API replacements)
- ⚙️ **Cross-Compilation**: Automate building for ARM and x86 targets
- 🧪 **Testing**: Validate apps on ARM emulators and real devices
- 🐳 **Containerization**: Build multi-architecture Docker images
- 📊 **Performance Analysis**: Compare ARM vs x86 performance metrics

## 🎯 Target Users

- Developers maintaining legacy x86 applications
- Teams deploying software to ARM-based servers or edge devices
- Organizations looking to leverage ARM's power efficiency and cost benefits

## 🚀 Quick Start

### Installation

#### Python SDK
```bash
cd sdk
pip install -e .
```

#### Go CLI
```bash
cd cli
go build -o m2arm main.go
# Or install globally
go install github.com/closedcodes/m2arm/cli@latest
```

#### Docker
```bash
docker-compose up m2arm-dev
```

### Usage Examples

```bash
# Scan your project for x86 dependencies
./m2arm scan /path/to/your/project

# Generate migration plan
./m2arm plan /path/to/your/project --target arm64

# Cross-compile for ARM
./m2arm compile /path/to/your/project --target arm64 --toolchain gcc-aarch64

# Test with QEMU emulation
./m2arm test /path/to/your/project --method qemu --arch arm64
```

### Python SDK Usage
```python
from m2arm import M2ARMCore, CodeScanner, Migrator

# Initialize the system
core = M2ARMCore()

# Scan project
scanner = CodeScanner()
issues = scanner.scan_directory("/path/to/project")

# Create and execute migration plan
migrator = Migrator()
plan = migrator.create_plan("/path/to/project")
result = migrator.execute_plan(plan)
```

## 📁 Project Structure

```
m2arm/
├── sdk/                    # Python SDK
│   ├── core.py            # Core orchestration
│   ├── scanner.py         # Code analysis engine
│   ├── migrator.py        # Migration planning & execution
│   ├── compiler.py        # Cross-compilation support
│   ├── tester.py          # ARM testing framework
│   └── optimizer.py       # Performance optimization
├── cli/                   # Go CLI
│   ├── main.go           # CLI entry point
│   └── cmd/              # Command implementations
├── examples/              # Example projects and use cases
│   └── cpp-simd/         # C++ SIMD migration example
├── docs/                 # Documentation
├── .github/              # CI/CD workflows
├── tools/                # Development and build tools
└── tests/                # Integration tests
```

## 🔧 Development

### Prerequisites
- Python 3.8+
- Go 1.19+
- CMake 3.25+
- Docker (optional)
- QEMU (for ARM emulation)

### Setup
```bash
# Clone repository
git clone https://github.com/closedcodes/m2arm.git
cd m2arm

# Install Python SDK
cd sdk && pip install -e . && cd ..

# Build Go CLI
cd cli && go build -o m2arm main.go && cd ..

# Run tests
cd sdk && pytest tests/
cd cli && go test ./...
```

### CI/CD Status
[![CI/CD Pipeline](https://github.com/closedcodes/m2arm/actions/workflows/ci.yml/badge.svg)](https://github.com/closedcodes/m2arm/actions/workflows/ci.yml)

The project includes comprehensive CI/CD pipelines with:
- Multi-platform testing (Linux, Windows, macOS)
- Cross-compilation for ARM64, ARMv7, x86_64
- Security scanning with proper permissions
- Docker multi-architecture builds
- Automated releases

> **Note**: Recent CI/CD improvements include updating deprecated GitHub Actions and fixing permission issues for security scanning.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## � Security

Please see our [Security Policy](SECURITY.md) for information about reporting vulnerabilities.

## �📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: https://github.com/closedcodes/m2arm
- **Issues**: https://github.com/closedcodes/m2arm/issues
- **Actions**: https://github.com/closedcodes/m2arm/actions
