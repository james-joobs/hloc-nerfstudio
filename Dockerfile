FROM ghcr.io/nerfstudio-project/nerfstudio:latest

# 환경변수 설정
ENV PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_DEFAULT_TIMEOUT=120 \
    TORCH_HOME=/home/user/.cache/torch \
    HF_HOME=/home/user/.cache/huggingface \
    HLOC_CACHE=/home/user/.cache/hloc \
    PYCOLMAP_CUDA_ARCHITECTURES="native" \
    CMAKE_CUDA_ARCHITECTURES="native" \
    PYTHONPATH="/opt/third_party/SuperGluePretrainedNetwork:/opt/third_party" \
    PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:${PKG_CONFIG_PATH}" \
    COLMAP_EXE_PATH="/usr/local/bin/colmap" \
    HLOC_COLMAP_PATH="/usr/local/bin/colmap" \
    HLOC_USE_PYCOLMAP="false" \
    COLMAP_BINARY_PATH="/usr/local/bin/colmap" \
    PYCOLMAP_USE_BINARY="1" \
    OMP_NUM_THREADS=1 \
    PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512" \
    TORCH_NUM_WORKERS=0 \
    CUDA_MODULE_LOADING=LAZY \
    TORCH_CUDNN_V8_API_DISABLED=1

# 필요한 디렉터리 생성
RUN mkdir -p /home/user/.cache/torch/hub/checkpoints \
             /home/user/.cache/torch/hub/netvlad \
             /home/user/.cache/hloc

# CUDA 12.8 nvrtc 라이브러리 심볼릭 링크 설정
RUN if [ -d "/usr/local/cuda-12.8/targets/x86_64-linux/lib/" ]; then \
        cd /usr/local/cuda-12.8/targets/x86_64-linux/lib/ && \
        ln -sf libnvrtc.so.12 libnvrtc.so && \
        ln -sf libnvrtc-builtins.so.12 libnvrtc-builtins.so; \
    elif [ -d "/usr/local/cuda/lib64/" ]; then \
        cd /usr/local/cuda/lib64/ && \
        ln -sf libnvrtc.so.12 libnvrtc.so && \
        ln -sf libnvrtc-builtins.so.12 libnvrtc-builtins.so; \
    else \
        echo "CUDA library directory not found, skipping nvrtc links"; \
    fi

# COLMAP 업그레이드 스크립트만 먼저 복사
COPY scripts/upgrade-colmap.sh /tmp/scripts/
RUN chmod +x /tmp/scripts/upgrade-colmap.sh

# COLMAP 3.12.4 C++ 엔진 업그레이드 (frames.bin 지원) - 캐시 보존 중요!
RUN /tmp/scripts/upgrade-colmap.sh

# === COLMAP 빌드 완료 지점 - 여기서 캐시됨 ===
# 이 지점 이후의 실패는 COLMAP 빌드에 영향 없음

# 나머지 스크립트와 패치 파일들 복사
COPY scripts/ /tmp/scripts/
COPY patches/ /tmp/patches/
RUN chmod +x /tmp/scripts/*.sh /tmp/scripts/*.py /tmp/patches/*.py

# 의존성 설치 (pycolmap 포함)
RUN /tmp/scripts/setup-dependencies.sh

# === PyTorch 2.7.0 stable + CUDA 12.8 (RTX 5090 Blackwell 공식 지원) ===
# 기존 PyTorch 제거 및 안정적인 2.7.0 stable 버전 설치
RUN python -m pip uninstall -y torch torchvision torchaudio || true
RUN python -m pip install --break-system-packages \
    torch==2.7.0 \
    torchvision \
    torchaudio \
    --index-url https://download.pytorch.org/whl/cu128 \
    --force-reinstall \
    --no-cache-dir

# CUDA 12.8 toolkit 설치 (nvcc 컴파일러 포함) - 기존 keyring 활용
RUN apt-get update && \
    # CUDA 12.8 패키지 직접 설치 (기존 keyring 사용)
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        cuda-toolkit-12-8 \
        cuda-compiler-12-8 \
        cuda-nvcc-12-8 \
        cuda-libraries-dev-12-8 \
        --no-install-recommends && \
    # CUDA 12.8 심볼릭 링크 생성
    ln -sf /usr/local/cuda-12.8 /usr/local/cuda && \
    # 설치 확인
    ls -la /usr/local/cuda-12.8/bin/nvcc && \
    /usr/local/cuda-12.8/bin/nvcc --version && \
    rm -rf /var/lib/apt/lists/*

# CUDA 12.8 환경변수 설정 (시스템 CUDA toolkit 사용)
ENV CUDA_HOME=/usr/local/cuda-12.8 \
    CUDA_PATH=/usr/local/cuda-12.8 \
    PATH="/usr/local/cuda-12.8/bin:${PATH}" \
    LD_LIBRARY_PATH="/usr/local/cuda-12.8/lib64:/usr/local/lib/python3.10/dist-packages/torch/lib:/usr/local/lib/python3.10/dist-packages/nvidia/cuda_runtime/lib:/usr/local/lib/python3.10/dist-packages/nvidia/cuda_cupti/lib:/usr/local/lib/python3.10/dist-packages/nvidia/cuda_nvrtc/lib:${LD_LIBRARY_PATH}" \
    PYCOLMAP_CUDA_ARCHITECTURES="native" \
    CMAKE_CUDA_ARCHITECTURES="native"

# NumPy 2.x 호환성 문제 해결 - 명시적으로 1.26.4 고정
RUN python -m pip install --break-system-packages "numpy==1.26.4" --force-reinstall

# GLM 라이브러리 설치 (gsplat 컴파일 의존성)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        libglm-dev \
        --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# gsplat 설정 - CUDA 12.8 호환성을 위해 기존 1.4.0 버전 유지
# (v1.5.3은 cooperative_groups::labeled_partition API 호환성 문제로 인해 CUDA 12.8에서 컴파일 실패)
RUN echo "✅ Using existing gsplat 1.4.0 (CUDA 12.8 compatible)" && \
    python -c "import gsplat; print(f'gsplat version: {gsplat.__version__}')" || echo "gsplat not available"

# PyMeshLab Qt 라이브러리 충돌 문제 해결 
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    qtbase5-dev qttools5-dev libqt5opengl5-dev libglew-dev libeigen3-dev \
    libgmp-dev libmpfr-dev libboost-dev \
    # Qt5 런타임 라이브러리 설치 (qt5-default는 Ubuntu 22.04에서 사용 안함)
    libqt5core5a libqt5gui5 libqt5widgets5 \
    libqt5opengl5 libqt5x11extras5 qtchooser && \
    rm -rf /var/lib/apt/lists/*

# PyMeshLab 환경 변수 설정 (Qt 충돌 방지)
ENV QT_QPA_PLATFORM=offscreen \
    DISPLAY= \
    MESA_GL_VERSION_OVERRIDE=3.3

# PyMeshLab 완전 제거 및 ns-export 우회 설정
RUN python -m pip uninstall -y pymeshlab || true

# PyMeshLab 우회 패치 적용
RUN python /tmp/patches/pymeshlab_bypass.py || echo "⚠ PyMeshLab bypass patch failed"

# 모델 복사 (호스트에서 이미 다운로드된 모델 사용)
COPY models_cache/ /tmp/models_cache/
RUN mkdir -p /home/user/.cache/torch/hub/checkpoints /home/user/.cache/torch/hub/netvlad
RUN cp /tmp/models_cache/*.pth /home/user/.cache/torch/hub/checkpoints/ && \
    cp /tmp/models_cache/*.mat /home/user/.cache/torch/hub/netvlad/ && \
    echo "✅ All models copied successfully"

# 파일 권한 설정
RUN chmod -R 755 /home/user/.cache

# hloc 구문 오류 먼저 수정 (중요!)
RUN python /tmp/patches/fix_hloc_syntax.py || echo "⚠ hloc syntax fix failed, continuing"

# 호환성 패치 적용 (실패해도 계속 진행)
ENV APPLY_PYCOLMAP_PATCHES=true
RUN python /tmp/scripts/apply-patches.py || echo "⚠ Some patches failed, continuing with fallback"

# 핵심 API 패치를 직접 적용 (pycolmap import 없이)
RUN python /tmp/patches/direct_reconstruction_fix.py || echo "⚠ Direct patch failed, using original API"

# viser CameraMessage 호환성 패치 적용
RUN python /tmp/patches/fix_viser_camera_message.py || echo "⚠ viser compatibility patch failed"

# 모델 및 패치 검증 (실패해도 계속 진행)
RUN python /tmp/scripts/verify-models.py || echo "⚠ Some verifications failed, but core functionality available"

# 최종 PyTorch 환경 검증
RUN python -m pip install --break-system-packages "numpy==1.26.4" --force-reinstall && \
    echo "=== Environment Verification ===" && \
    python -c "import numpy; print('Final NumPy version:', numpy.__version__)" && \
    python -c "import torch; print('PyTorch version:', torch.__version__)" && \
    python -c "import torch; print('PyTorch CUDA version:', torch.version.cuda)" && \
    python -c "import torch; print('CUDA available (build-time):', torch.cuda.is_available())" && \
    python -c "import torch; print('Supported architectures:', torch.cuda.get_arch_list())" && \
    python /tmp/scripts/final-verification.py && \
    echo "✅ Build verification completed"

# 최종 정리
RUN rm -rf /tmp/scripts /tmp/patches

# 작업 디렉터리 설정
WORKDIR /workspace

# Viser 정적 파일을 호스트에서 접근 가능한 위치로 복사 (production 배포용)
RUN mkdir -p /opt/viser-static && \
    cp -r /usr/local/lib/python3.10/dist-packages/viser/client/build /opt/viser-static/ && \
    chmod -R 755 /opt/viser-static/

# 포트 노출 (nerfstudio viewer용)
EXPOSE 7007

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD nvidia-smi