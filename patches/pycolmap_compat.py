#!/usr/bin/env python3
"""
pycolmap 호환성 패치 스크립트
hloc과 pycolmap 간의 API 호환성 문제 해결
최신 pycolmap >= 0.8.0 버전에서는 대부분의 호환성 문제가 해결되어
패치가 필요하지 않을 수 있음
"""

import sys
from pathlib import Path


def check_pycolmap_version():
    """pycolmap 버전 확인"""
    try:
        import pycolmap
        version = pycolmap.__version__
        major, minor = map(int, version.split('.')[:2])
        
        print(f"pycolmap version: {version}")
        
        # 0.8.0 이상이면 패치 불필요
        if major > 0 or (major == 0 and minor >= 8):
            print("✓ Modern pycolmap version detected, no compatibility patch needed")
            return True, False  # (success, needs_patch)
        else:
            print("⚠ Old pycolmap version detected, applying compatibility patch")
            return True, True  # (success, needs_patch)
            
    except Exception as e:
        print(f"ERROR checking pycolmap version: {e}")
        return False, False


def patch_hloc_reconstruction():
    """hloc reconstruction.py의 pycolmap 호환성 패치 (구 버전용)"""
    try:
        # 먼저 버전 체크
        success, needs_patch = check_pycolmap_version()
        if not success:
            return False
        if not needs_patch:
            return True
        
        import hloc.reconstruction as hloc_recon
        recon_file = Path(hloc_recon.__file__)
        
        print(f"Patching hloc reconstruction: {recon_file}")
        
        # 파일 내용 읽기
        with open(recon_file, 'r') as f:
            content = f.read()
        
        # 이미 패치되었는지 확인
        if 'PYCOLMAP_COMPATIBILITY_PATCH' in content:
            print("✓ pycolmap compatibility patch already applied")
            return True
        
        # import pycolmap 라인 찾기
        lines = content.split('\n')
        import_line_index = -1
        
        for i, line in enumerate(lines):
            if 'import pycolmap' in line and not line.strip().startswith('#'):
                import_line_index = i
                break
        
        if import_line_index < 0:
            print("⚠ Could not find 'import pycolmap' line")
            return False
        
        # 패치 코드 생성
        patch_lines = [
            '',
            '# PYCOLMAP_COMPATIBILITY_PATCH',
            '# Backup original function FIRST',
            '_original_import_images = pycolmap.import_images',
            '',
            'def _patched_import_images(database_path, image_path, camera_mode, image_list=None, options=None, **kwargs):',
            '    """Wrapper for pycolmap.import_images that converts Path objects to strings"""',
            '    # Convert Path objects to strings', 
            '    database_str = str(database_path) if hasattr(database_path, "__fspath__") else database_path',
            '    image_str = str(image_path) if hasattr(image_path, "__fspath__") else image_path',
            '    ',
            '    # Handle kwargs mapping for API compatibility',
            '    if "image_names" in kwargs:',
            '        image_list = kwargs.pop("image_names", [])',
            '    if "options" in kwargs:',
            '        options = kwargs.pop("options", None)',
            '    ',
            '    # Create default options if not provided',
            '    if options is None:',
            '        import pycolmap',
            '        options = pycolmap.ImageReaderOptions()',
            '    ',
            '    # Ensure image_list is provided (empty list if None)',
            '    if image_list is None:',
            '        image_list = []',
            '    ',
            '    # Call with proper positional arguments',
            '    return _original_import_images(database_str, image_str, camera_mode, image_list, options)',
            '',
            '# Replace with patched version',
            'pycolmap.import_images = _patched_import_images',
            ''
        ]
        
        # import 라인 다음에 패치 코드 삽입
        lines[import_line_index+1:import_line_index+1] = patch_lines
        
        # 파일 저장
        patched_content = '\n'.join(lines)
        with open(recon_file, 'w') as f:
            f.write(patched_content)
        
        print("✓ pycolmap compatibility patch applied successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: pycolmap compatibility patch failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=== Applying pycolmap compatibility patch ===")
    
    if patch_hloc_reconstruction():
        print("✅ pycolmap compatibility patch completed successfully")
        sys.exit(0)
    else:
        print("❌ pycolmap compatibility patch failed")
        sys.exit(1)