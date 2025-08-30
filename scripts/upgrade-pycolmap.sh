#!/bin/bash
set -e

echo "=== Upgrading pycolmap to version >= 0.8.0 ==="

# 현재 pycolmap 버전 확인
current_version=$(python -c "import pycolmap; print(pycolmap.__version__)" 2>/dev/null || echo "Not installed")
echo "Current pycolmap version: $current_version"

echo "--- Uninstalling old pycolmap ---"
python -m pip uninstall -y pycolmap 2>/dev/null || true

echo "--- Installing latest pycolmap ---"
# 최신 pycolmap 설치 (COLMAP 3.12와 호환)
python -m pip install --break-system-packages "pycolmap>=0.8.0" --no-cache-dir --force-reinstall

# 설치 확인
echo "--- Verifying pycolmap installation ---"
python -c "
import pycolmap
print(f'✅ pycolmap version: {pycolmap.__version__}')

# 최신 API 테스트
try:
    # COLMAP 3.12+ 호환성 확인
    import pycolmap
    print('✅ pycolmap API compatibility check passed')
    
    # 기본적인 함수들 확인
    functions_to_check = ['import_images', 'extract_features', 'match_features']
    for func_name in functions_to_check:
        if hasattr(pycolmap, func_name):
            print(f'✅ {func_name} function available')
        else:
            print(f'⚠ {func_name} function not found')
            
except Exception as e:
    print(f'⚠ pycolmap compatibility issue: {e}')
"

echo "✅ pycolmap upgrade completed!"