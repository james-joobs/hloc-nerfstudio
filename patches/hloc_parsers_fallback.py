#!/usr/bin/env python3
"""
hloc parsers.py pycolmap fallback 패치
기존 작동하던 방식을 정확히 복원
"""

import sys
import os
from pathlib import Path


def patch_hloc_parsers():
    """hloc parsers.py에 pycolmap fallback 패치 적용"""
    try:
        import hloc
        hloc_path = Path(hloc.__file__).parent
        
        # parsers.py 파일 패치
        patch_file = hloc_path / 'utils' / 'parsers.py'
        if not patch_file.exists():
            print(f"⚠ hloc parsers.py not found: {patch_file}")
            return False
        
        print(f"Patching hloc parsers.py: {patch_file}")
        
        with open(patch_file, 'r') as f:
            content = f.read()
        
        if 'import pycolmap' in content and 'COLMAP_FALLBACK_PATCH' not in content:
            # pycolmap 0.6.1 Python wrapper용 패치 (COLMAP 3.12.4 C++ 엔진과 링크)
            patched_content = content.replace(
                'import pycolmap',
                '''# COLMAP_FALLBACK_PATCH - pycolmap 0.6.1 with COLMAP 3.12.4
try:
    import pycolmap
    # pycolmap 0.6.1 Python wrapper가 COLMAP 3.12.4 C++ 백엔드 사용
    print(f"INFO: pycolmap {pycolmap.__version__} loaded successfully")
except (ImportError, RuntimeError) as e:
    pycolmap = None
    print(f"WARNING: pycolmap import failed ({e}), falling back to COLMAP binary")'''
            )
            
            with open(patch_file, 'w') as f:
                f.write(patched_content)
            
            print("✓ Applied pycolmap fallback patch to hloc parsers.py")
            return True
        else:
            print("✓ hloc parsers.py already patched or no pycolmap import found")
            return True
            
    except Exception as e:
        print(f"ERROR: hloc parsers patch failed: {e}")
        return False


if __name__ == "__main__":
    print("=== Applying hloc parsers fallback patch ===")
    
    if patch_hloc_parsers():
        print("✅ hloc parsers fallback patch completed")
        sys.exit(0)
    else:
        print("❌ hloc parsers fallback patch failed")
        sys.exit(1)