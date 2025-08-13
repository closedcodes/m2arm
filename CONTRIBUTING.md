# Contributing to M2ARM

Thank you for your interest in contributing to M2ARM! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.8+ (for SDK development)
- Go 1.19+ (for CLI development)
- Git

### Setting Up the Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/m2arm/m2arm.git
   cd m2arm
   ```

2. **Python SDK Setup:**
   ```bash
   cd sdk
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Go CLI Setup:**
   ```bash
   cd cli
   go mod download
   go build -o m2arm main.go
   ```

### Running Tests

**Python SDK Tests:**
```bash
cd sdk
python -m pytest tests/
```

**Go CLI Tests:**
```bash
cd cli
go test ./...
```

## Project Structure

```
m2arm/
├── sdk/                    # Python SDK
│   ├── __init__.py
│   ├── core.py            # Main orchestrator
│   ├── scanner.py         # Code scanning
│   ├── migrator.py        # Migration planning/execution
│   ├── compiler.py        # Cross-compilation
│   ├── tester.py          # ARM testing
│   └── optimizer.py       # Performance optimization
├── cli/                   # Go CLI
│   ├── main.go
│   ├── cmd/               # CLI commands
│   └── internal/          # Internal packages
├── examples/              # Example projects
├── docs/                  # Documentation
├── tools/                 # Development tools
└── tests/                 # Integration tests
```

## Contributing Guidelines

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Maximum line length: 88 characters

**Go:**
- Follow Go conventions
- Use `gofmt` and `golint`
- Write meaningful variable names
- Add comments for exported functions

### Git Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit with descriptive messages
7. Push to your fork
8. Create a Pull Request

### Commit Messages

Use conventional commit format:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding missing tests
- `chore`: Changes to build process or auxiliary tools

### Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure CI passes
4. Request review from maintainers
5. Address review feedback
6. Squash commits before merge

## Areas for Contribution

### High Priority

- **ARM NEON mappings**: Expand x86 to ARM NEON intrinsic mappings
- **Build system support**: Add support for more build systems
- **Language support**: Add support for more programming languages
- **Testing frameworks**: Improve ARM testing capabilities

### Medium Priority

- **Performance optimization**: ARM-specific optimization strategies
- **Documentation**: User guides and API documentation
- **CLI UX**: Improve command-line interface usability
- **Error handling**: Better error messages and recovery

### Low Priority

- **Platform support**: Additional ARM platforms
- **Integration**: CI/CD pipeline integrations
- **Monitoring**: Performance monitoring tools

## Adding New Features

### SDK Components

When adding new SDK functionality:

1. Create the module in `/sdk/`
2. Add to `__init__.py` exports
3. Write comprehensive tests
4. Update documentation
5. Add CLI commands if needed

### CLI Commands

When adding new CLI commands:

1. Create command file in `/cli/cmd/`
2. Add to root command
3. Include help text and examples
4. Add corresponding SDK calls
5. Write tests

### Examples

When adding examples:

1. Create directory in `/examples/`
2. Include complete project
3. Add README with M2ARM usage
4. Test migration workflow
5. Document expected results

## Testing

### Test Coverage

- Aim for >80% test coverage
- Include unit, integration, and end-to-end tests
- Test error conditions and edge cases
- Verify cross-platform compatibility

### Test Data

- Use realistic code samples
- Include various architectures and languages
- Cover both simple and complex scenarios
- Provide expected migration results

## Documentation

### User Documentation

- Keep README up to date
- Write clear installation instructions
- Provide comprehensive examples
- Document common issues and solutions

### Developer Documentation

- Document internal APIs
- Explain design decisions
- Provide architecture overview
- Include contribution guidelines

## Release Process

### Version Numbering

Follow Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH
- Breaking changes increment MAJOR
- New features increment MINOR
- Bug fixes increment PATCH

### Release Checklist

1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Build and test distributions
5. Create GitHub release
6. Update documentation

## Getting Help

### Communication Channels

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: General questions and ideas
- Email: team@m2arm.dev

### Resources

- [ARM Developer Documentation](https://developer.arm.com/)
- [NEON Intrinsics Reference](https://developer.arm.com/architectures/instruction-sets/intrinsics/)
- [Cross-compilation Guide](https://wiki.osdev.org/Cross-Compiler)

## License

By contributing to M2ARM, you agree that your contributions will be licensed under the MIT License.
