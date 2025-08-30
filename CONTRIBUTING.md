# Contributing to HLOC-NeRFStudio

We love your input! We want to make contributing to HLOC-NeRFStudio as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Requests Process

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the Docker build passes.
5. Make sure your code lints.
6. Issue that pull request!

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/hloc-nerfstudio.git
cd hloc-nerfstudio

# Build and test locally
./setup.sh

# Test the container
docker-compose up -d hloc-nerfstudio
docker-compose exec hloc-nerfstudio bash
```

### Testing Your Changes

Before submitting a PR, please ensure:

1. **Docker Build Test**:
   ```bash
   docker build -t hloc-nerfstudio:test .
   ```

2. **Functionality Test**:
   ```bash
   docker run --rm --gpus all hloc-nerfstudio:test python -c "import hloc; print('HLOC OK')"
   docker run --rm --gpus all hloc-nerfstudio:test ns-train --help
   ```

3. **Integration Test**:
   ```bash
   # Test with sample data if available
   docker-compose exec hloc-nerfstudio ns-train nerfacto --help
   ```

## Code Style

- Use clear, descriptive variable names
- Comment complex logic
- Keep Docker layers optimized for caching
- Follow existing patterns in the codebase

### Docker Best Practices

- Minimize layer count where possible
- Use multi-stage builds for complex installations
- Clean up package caches and temporary files
- Pin version numbers for reproducibility

### Patch Development

When adding compatibility patches:

1. Place patch files in the `patches/` directory
2. Name patches descriptively (e.g., `fix_numpy_compatibility.py`)
3. Include error handling with fallbacks
4. Document what the patch fixes in comments

## Bug Reports

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Feature Requests

We track feature requests as [GitHub issues](https://github.com/yourusername/hloc-nerfstudio/issues). 

**Great Feature Requests** include:

- **Is your feature request related to a problem?** A clear description of the problem.
- **Describe the solution you'd like** - What you want to happen.
- **Describe alternatives you've considered** - Other solutions you considered.
- **Additional context** - Screenshots, mockups, etc.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## References

This document was adapted from the open-source contribution guidelines for:
- [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md)
- [NeRFStudio Contributing Guide](https://github.com/nerfstudio-project/nerfstudio/blob/main/CONTRIBUTING.md)