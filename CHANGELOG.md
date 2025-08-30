# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of HLOC-NeRFStudio integration
- Production-ready Docker container with all dependencies
- COLMAP 3.12.4 with frames.bin support
- Comprehensive HLOC compatibility patches
- NumPy 1.26.4 compatibility fixes for NeRFStudio
- PyMeshLab conflict resolution with Qt bypass
- Pre-downloaded models (SuperPoint, LightGlue, NetVLAD, etc.)
- Docker Compose configuration for easy deployment
- One-click setup script (`setup.sh`)
- Comprehensive README with usage examples
- GitHub issue templates and PR templates
- Contributing guidelines

### Fixed
- HLOC syntax errors and import issues
- PyColmap compatibility with COLMAP binary mode
- Viser CameraMessage compatibility issues
- NumPy 2.x compatibility problems with NeRFStudio
- PyMeshLab Qt library conflicts
- CUDA memory allocation issues
- Docker build caching optimization

### Changed
- Removed Gradio integration (focus on core NeRFStudio functionality)
- Optimized Dockerfile for better layer caching
- Updated documentation with comprehensive examples
- Improved error handling with fallback mechanisms

## [1.0.0] - 2024-08-30

### Added
- Initial stable release
- All core features implemented and tested
- Complete documentation and setup guides