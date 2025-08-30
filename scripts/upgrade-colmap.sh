#!/bin/bash
set -e

echo "=== Upgrading COLMAP to version >= 3.12 ==="

# 현재 COLMAP 버전 확인
if command -v colmap >/dev/null 2>&1; then
    current_version=$(colmap -h 2>&1 | grep -o "COLMAP [0-9]\+\.[0-9]\+\.[0-9]\+" | head -1)
    echo "Current COLMAP version: $current_version"
fi

# 기존 COLMAP 제거 (필요시)
echo "--- Removing old COLMAP installation ---"
apt-get remove --purge -y colmap 2>/dev/null || true

# 필수 의존성 설치 (Ninja, ccache 추가)
echo "--- Installing build dependencies ---"
apt-get update
apt-get install -y \
    git \
    cmake \
    ninja-build \
    ccache \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libboost-test-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgtest-dev \
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev \
    libsuitesparse-dev

echo "--- Building Ceres Solver 2.2.0 for pycolmap compatibility ---"
# ccache 활성화 (빌드 캐싱으로 재빌드 시 매우 빠름)
export PATH="/usr/lib/ccache:$PATH"
export CCACHE_DIR=/tmp/ccache
export CCACHE_MAXSIZE=5G
mkdir -p $CCACHE_DIR

cd /tmp

# Ceres Solver 2.2.0 빌드 (최신 안정 버전)
CERES_VERSION="2.2.0"
echo "Building Ceres Solver ${CERES_VERSION}..."
git clone --depth=1 --branch ${CERES_VERSION} https://github.com/ceres-solver/ceres-solver.git ceres-${CERES_VERSION}
cd "ceres-${CERES_VERSION}"

mkdir -p build && cd build
cmake .. \
    -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTING=OFF \
    -DBUILD_DOCUMENTATION=OFF \
    -DBUILD_EXAMPLES=OFF \
    -DBUILD_BENCHMARKS=OFF \
    -DCMAKE_INSTALL_PREFIX=/usr/local

echo "Building with Ninja (much faster)..."
START_TIME=$(date +%s)
ninja -v  # -v for verbose to see progress
ninja install
END_TIME=$(date +%s)
echo "✓ Ceres build completed in $((END_TIME - START_TIME)) seconds"
ldconfig  # 라이브러리 캐시 업데이트

echo "--- Downloading and building COLMAP 3.12.4 ---"
cd /tmp

# COLMAP 3.12.4 다운로드 (git clone이 더 안정적)
COLMAP_VERSION="3.12.4"
echo "Cloning COLMAP ${COLMAP_VERSION} from GitHub..."
git clone --depth=1 --branch ${COLMAP_VERSION} https://github.com/colmap/colmap.git colmap-${COLMAP_VERSION}
cd "colmap-${COLMAP_VERSION}"

# 빌드 디렉터리 생성
mkdir build
cd build

# CMake 설정 (새로 빌드한 Ceres 2.2.0 사용)
echo "--- Configuring COLMAP build with Ninja ---"
cmake .. \
    -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DCUDA_ENABLED=ON \
    -DGUI_ENABLED=OFF \
    -DOPENMP_ENABLED=ON \
    -DCGAL_ENABLED=ON \
    -DLSD_ENABLED=ON \
    -DCeres_ROOT=/usr/local \
    -DCMAKE_PREFIX_PATH=/usr/local

# 컴파일 (Ninja는 자동으로 병렬 빌드)
echo "--- Building COLMAP with Ninja (much faster) ---"
START_TIME=$(date +%s)
ninja -v  # -v for verbose to see progress
END_TIME=$(date +%s)
echo "✓ COLMAP build completed in $((END_TIME - START_TIME)) seconds"

# 설치
echo "--- Installing COLMAP ---"
ninja install

# 설치 확인
echo "--- Verifying COLMAP installation ---"
/usr/local/bin/colmap -h | head -5

# 새 버전 확인
new_version=$(/usr/local/bin/colmap -h 2>&1 | grep -o "COLMAP [0-9]\+\.[0-9]\+\.[0-9]\+" | head -1)
echo "✅ New COLMAP version: $new_version"

# 임시 파일 정리
cd /
rm -rf /tmp/colmap*

# 라이브러리 경로 업데이트
ldconfig

echo "✅ COLMAP upgrade completed!"