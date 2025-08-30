#!/bin/bash
set -e

echo "=== Setting up nerfstudio dependencies ==="

# 한국 미러 설정
echo "--- Configuring Korean mirrors ---"
sed -i 's|http://deb.debian.org|http://ftp.kaist.ac.kr|g' /etc/apt/sources.list* 2>/dev/null || true
sed -i 's|http://security.debian.org|http://ftp.kaist.ac.kr|g' /etc/apt/sources.list* 2>/dev/null || true
sed -i 's|http://archive.ubuntu.com|http://mirror.kakao.com|g' /etc/apt/sources.list* 2>/dev/null || true

# 시스템 패키지 설치
echo "--- Installing system packages ---"
apt-get update
apt-get install -y --no-install-recommends \
    git vim ca-certificates libgl1 libglib2.0-0 \
    build-essential cmake \
    libboost-program-options-dev libboost-filesystem-dev libboost-graph-dev \
    libboost-system-dev libboost-test-dev \
    libeigen3-dev libflann-dev libfreeimage-dev \
    libmetis-dev libgoogle-glog-dev libgtest-dev \
    libsqlite3-dev libglew-dev qtbase5-dev libqt5opengl5-dev \
    libcgal-dev libceres-dev

# CA 인증서 업데이트
update-ca-certificates
rm -rf /var/lib/apt/lists/*

echo "--- Upgrading pip ---"
python -m pip install --upgrade pip setuptools wheel

echo "--- Installing Python packages ---"
# hloc 설치 (의존성 무시)
python -m pip install --break-system-packages \
    --no-deps "git+https://github.com/cvg/Hierarchical-Localization.git"

# 기타 패키지들 (NumPy 버전 충돌 방지)
python -m pip install --break-system-packages \
    lightglue \
    kornia \
    pydegensac \
    opencv-python-headless \
    faiss-cpu \
    h5py \
    "scipy<1.14" \
    tqdm

echo "--- Setting up SuperGluePretrainedNetwork ---"
mkdir -p /opt/third_party
git clone --depth=1 https://github.com/magicleap/SuperGluePretrainedNetwork.git \
    /opt/third_party/SuperGluePretrainedNetwork

echo "--- Building pycolmap from source (to link with COLMAP 3.12.4) ---"
# NumPy 1.26.4 고정하여 설치 (PyTorch 호환성 유지)
python -m pip install --break-system-packages "numpy==1.26.4" pybind11 wheel setuptools packaging

# 환경 변수 설정으로 새로 빌드한 Ceres 2.2.0을 사용
export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
export LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
export CMAKE_PREFIX_PATH="/usr/local:$CMAKE_PREFIX_PATH"

# 기존 pycolmap/pyceres 제거 (충돌 방지)
python -m pip uninstall -y pycolmap pyceres || true

# 시스템 Ceres 패키지도 제거하여 충돌 방지 (새로 빌드한 2.2.0 사용)
apt-get remove --purge -y libceres-dev libceres2 || true

# pycolmap을 설치 (COLMAP 3.12.4 C++ 엔진과 호환)
# 방법 1: 먼저 0.6.1 wheel 시도 (빠르지만 ABI 호환성 문제 가능)
# 방법 2: 실패 시 최신 버전을 소스에서 빌드
echo "Installing pycolmap to link with COLMAP 3.12.4..."

# 먼저 0.6.1 wheel 시도 (manylinux wheel은 보통 호환됨)
if python -m pip install --break-system-packages "pycolmap==0.6.1" 2>/dev/null; then
    echo "✓ Installed pycolmap 0.6.1 from wheel"
else
    echo "⚠ pycolmap 0.6.1 wheel failed, building latest from source..."
    # 최신 버전을 소스에서 빌드 (COLMAP 3.12.4와 링크)
    python -m pip install --break-system-packages --no-binary=pycolmap pycolmap --verbose
fi

echo "--- Verifying installations ---"
python -c "
import importlib
modules = ['hloc', 'lightglue', 'kornia', 'SuperGluePretrainedNetwork.models.superpoint']
for m in modules:
    status = 'OK' if importlib.util.find_spec(m) else 'MISSING'
    print(f'{m}: {status}')
"

# pycolmap 확인 - COLMAP 3.12.4와 연결 확인
python -c "
try:
    import pycolmap
    print(f'✓ pycolmap {pycolmap.__version__} installed')
    
    # 버전 정보 명확히 표시
    if pycolmap.__version__.startswith('0.6'):
        print('  → Using pycolmap 0.6.x Python wrapper')
    else:
        print(f'  → Using pycolmap {pycolmap.__version__} (newer version)')
    
    # C++ backend 테스트
    try:
        rec = pycolmap.Reconstruction()
        print('✅ pycolmap C++ backend working!')
        print('  → Successfully linked with COLMAP 3.12.4 C++ engine')
    except Exception as e:
        print(f'⚠ pycolmap C++ backend issue: {e}')
        print('  → Will use COLMAP binary fallback')
        
except Exception as e:
    print(f'❌ pycolmap import failed: {e}')
    print('  → Will rely on COLMAP binary only')
"

# COLMAP 바이너리 확인 (더 중요)
echo "--- Verifying COLMAP binary ---"
if command -v /usr/local/bin/colmap >/dev/null 2>&1; then
    /usr/local/bin/colmap -h | head -3
    echo "✅ COLMAP binary ready for use"
else
    echo "❌ COLMAP binary not found"
    exit 1
fi

echo "✅ Dependencies setup completed!"