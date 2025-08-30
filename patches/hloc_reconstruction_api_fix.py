#!/usr/bin/env python3
"""
hloc reconstruction.py pycolmap API 호환성 패치
pycolmap 0.6.1 Python wrapper의 API 변경사항 수정
(COLMAP 3.12.4 C++ 엔진과 링크된 pycolmap 0.6.1 사용)
"""

import sys
import os
from pathlib import Path


def patch_hloc_reconstruction():
    """hloc reconstruction.py의 pycolmap API 호출을 최신 버전에 맞게 수정"""
    try:
        # hloc import 없이 직접 경로 추정
        hloc_path = Path('/usr/local/lib/python3.10/dist-packages/hloc')
        if not hloc_path.exists():
            # 대안 경로들 시도
            for possible_path in [
                Path('/usr/local/lib/python3.10/site-packages/hloc'),
                Path('/opt/conda/lib/python3.10/site-packages/hloc'),
            ]:
                if possible_path.exists():
                    hloc_path = possible_path
                    break
        
        if not hloc_path.exists():
            print(f"⚠ hloc directory not found")
            return False
        
        # reconstruction.py 파일 패치
        patch_file = hloc_path / 'reconstruction.py'
        if not patch_file.exists():
            print(f"⚠ hloc reconstruction.py not found: {patch_file}")
            return False
        
        print(f"Patching hloc reconstruction.py: {patch_file}")
        
        with open(patch_file, 'r') as f:
            content = f.read()
        
        if 'PYCOLMAP_API_FIX_PATCH' not in content:
            # image_names를 image_list로 변경
            original_call = '''pycolmap.import_images(
            database_path,
            image_dir,
            camera_mode,
            image_names=image_list or [],
            options=options,
        )'''
            
            patched_call = '''# PYCOLMAP_API_FIX_PATCH - pycolmap 0.6.1 API compatibility
        pycolmap.import_images(
            database_path=str(database_path),       # ✅ str로 캐스팅
            image_path=str(image_dir),              # ✅ str로 캐스팅  
            camera_mode=camera_mode,
            image_list=list(image_list or []),      # ✅ image_names → image_list 변경
            options=options,
        )'''
            
            patched_content = content.replace(original_call, patched_call)
            
            if patched_content != content:
                with open(patch_file, 'w') as f:
                    f.write(patched_content)
                
                print("✓ Applied pycolmap API fix patch to hloc reconstruction.py")
                print("  → Changed image_names to image_list parameter")
                print("  → Added str() casting for Path objects")
                return True
            else:
                print("⚠ Could not find the expected pycolmap.import_images call pattern")
                return False
        else:
            print("✓ hloc reconstruction.py already patched")
            return True
            
    except Exception as e:
        print(f"ERROR: hloc reconstruction API fix failed: {e}")
        return False


def main():
    """메인 함수"""
    if patch_hloc_reconstruction():
        return True
    else:
        return False


if __name__ == "__main__":
    print("=== Applying hloc reconstruction API fix patch ===")
    
    if main():
        print("✅ hloc reconstruction API fix patch completed")
        sys.exit(0)
    else:
        print("❌ hloc reconstruction API fix patch failed")
        sys.exit(1)