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

```bash
# Install the CLI
curl -sSL https://get.m2arm.dev | bash

# Scan your project
m2arm scan /path/to/your/project

# Generate migration plan
m2arm plan --target arm64

# Execute migration
m2arm migrate --apply
```

## 📁 Project Structure

```
m2arm/
├── sdk/                    # Python SDK
├── cli/                    # Go CLI
├── examples/               # Example projects and use cases
├── docs/                   # Documentation
├── tools/                  # Development and build tools
└── tests/                  # Integration tests
```

## 🛠️ Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
