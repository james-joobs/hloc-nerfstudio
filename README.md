# HLOC-NeRFStudio: Advanced 3D Reconstruction with NeRFStudio

🚀 **Production-ready Docker container for NeRFStudio with HLOC, COLMAP, and all essential 3D reconstruction tools**

This repository provides a comprehensive, pre-configured Docker environment that solves common compatibility issues and setup challenges when working with NeRFStudio, HLOC, COLMAP, and related 3D reconstruction tools.

## ✨ Key Features

### 🔧 **Pre-solved Compatibility Issues**
- ✅ **COLMAP 3.12.4** with frames.bin support (C++ engine)
- ✅ **HLOC** with syntax fixes and PyColmap compatibility patches
- ✅ **NumPy 1.26.4** compatibility (fixes NeRFStudio v2.x issues)
- ✅ **PyMeshLab** conflicts resolved with Qt bypass patches
- ✅ **Viser CameraMessage** compatibility patches applied

### 🏗️ **Advanced Build System**
- 🐳 **Multi-stage Docker build** with intelligent caching
- 📦 **Pre-downloaded models** (SuperPoint, LightGlue, NetVLAD, etc.)
- 🔄 **Automated dependency management**
- 🛠️ **Smart fallback mechanisms** for robust builds

### 📚 **Comprehensive Tool Integration**
- **NeRFStudio**: Latest stable version with all extensions
- **HLOC**: Hierarchical localization with all feature extractors
- **COLMAP**: Structure-from-Motion and Multi-View Stereo
- **LightGlue**: State-of-the-art feature matching
- **SuperPoint/SuperGlue**: Deep feature extraction and matching

## 🚀 Quick Start

### Prerequisites
- Docker with NVIDIA Container Runtime
- NVIDIA GPU with CUDA support
- Docker Compose

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/hloc-nerfstudio.git
cd hloc-nerfstudio
```

### 2. Build and Run
```bash
# Quick setup (recommended)
./setup.sh

# Or manually
docker-compose build hloc-nerfstudio
docker-compose up -d hloc-nerfstudio
```

### 3. Access the Container
```bash
# Enter the container
docker-compose exec hloc-nerfstudio bash

# Test installation
ns-train nerfacto --help
python -c "import hloc; print('HLOC ready!')"
```

### 4. Start Training
```bash
# Inside the container
ns-train nerfacto --data /workspace/data/your_scene

# View training progress
ns-viewer --load-config /workspace/outputs/your_scene/nerfacto/config.yml
```

Access the viewer at: **http://localhost:7007**

## 📂 Project Structure

```
hloc-nerfstudio/
├── Dockerfile              # Production-ready multi-stage build
├── docker-compose.yml      # Container orchestration
├── setup.sh               # One-click setup script
├── download_models.sh     # Pre-trained model downloader
├── scripts/               # Build and setup scripts
│   ├── upgrade-colmap.sh  # COLMAP C++ engine installer
│   ├── setup-dependencies.sh
│   └── verify-models.py
├── patches/               # Compatibility patches
│   ├── fix_hloc_syntax.py
│   ├── pymeshlab_bypass.py
│   └── fix_viser_camera_message.py
└── README.md             # This file
```

## 🔧 Advanced Usage

### Custom Model Training
```bash
# Custom NeRFStudio method
ns-train nerfacto \
  --data /workspace/data/your_scene \
  --output-dir /workspace/outputs \
  --viewer.websocket-port 7007

# With HLOC feature extraction
python -c "
import hloc
from hloc import extract_features, match_features
# Your HLOC pipeline here
"
```

### COLMAP Integration
```bash
# Inside container - COLMAP is ready to use
colmap --help

# Feature extraction with HLOC
python -c "
from hloc.utils.read_write_model import read_model
from hloc.utils.database import COLMAPDatabase
# Your SfM pipeline here
"
```

### Model Export
```bash
# Export to common formats
ns-export poisson --load-config /workspace/outputs/scene/config.yml
ns-export mesh --load-config /workspace/outputs/scene/config.yml
```

## 🐛 Troubleshooting

### Common Issues

**Q: COLMAP binary not found**
```bash
# Check COLMAP installation
echo $COLMAP_EXE_PATH
colmap --version
```

**Q: HLOC import errors**
```bash
# Verify HLOC installation
python -c "import hloc; print(hloc.__file__)"
```

**Q: NumPy compatibility issues**
```bash
# Check NumPy version (should be 1.26.4)
python -c "import numpy; print(numpy.__version__)"
```

**Q: CUDA out of memory**
```bash
# Adjust batch size in training
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
```

### Debug Mode
```bash
# Run with debug output
docker-compose up hloc-nerfstudio  # (without -d flag)

# Check logs
docker-compose logs -f hloc-nerfstudio
```

## 🏗️ Development

### Building from Source
```bash
# Build with custom tag
docker build -t hloc-nerfstudio:custom .

# Build with no cache
docker build --no-cache -t hloc-nerfstudio:fresh .
```

### Adding Custom Patches
1. Add your patch file to `patches/`
2. Update `Dockerfile` to apply the patch
3. Rebuild the container

### Pre-downloading Additional Models
```bash
# Modify download_models.sh to include your models
./download_models.sh
```

## 📊 Performance Tips

### GPU Optimization
- Use `--mixed-precision` for faster training
- Adjust `--pipeline.model.num-rays-per-chunk` based on GPU memory
- Enable `--pipeline.model.use-appearance-embedding false` for faster inference

### Memory Management
- Use `export OMP_NUM_THREADS=1` for CPU efficiency
- Set `TORCH_NUM_WORKERS=0` for Docker environments
- Enable `CUDA_MODULE_LOADING=LAZY` for faster startup

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Test your changes with the build system
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [NeRFStudio Team](https://github.com/nerfstudio-project/nerfstudio) for the amazing framework
- [HLOC Authors](https://github.com/cvg/Hierarchical-Localization) for hierarchical localization
- [COLMAP Authors](https://colmap.github.io/) for structure-from-motion
- [LightGlue Team](https://github.com/cvg/LightGlue) for feature matching

## 🔗 Related Projects

- [NeRFStudio](https://github.com/nerfstudio-project/nerfstudio)
- [HLOC](https://github.com/cvg/Hierarchical-Localization)
- [COLMAP](https://github.com/colmap/colmap)
- [LightGlue](https://github.com/cvg/LightGlue)

---

**⭐ Star this repository if it helps your 3D reconstruction projects!**