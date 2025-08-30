#!/usr/bin/env python3
"""
Direct hloc reconstruction.py API fix
pycolmap import 없이 직접 파일 수정
"""

import sys
from pathlib import Path


def patch_reconstruction_directly():
    """hloc reconstruction.py를 직접 패치"""
    
    # 가능한 hloc 경로들
    possible_paths = [
        Path('/usr/local/lib/python3.10/dist-packages/hloc/reconstruction.py'),
        Path('/usr/local/lib/python3.10/site-packages/hloc/reconstruction.py'),
        Path('/opt/conda/lib/python3.10/site-packages/hloc/reconstruction.py'),
    ]
    
    reconstruction_file = None
    for path in possible_paths:
        if path.exists():
            reconstruction_file = path
            break
    
    if not reconstruction_file:
        print("⚠ hloc reconstruction.py not found in expected locations")
        return False
        
    print(f"Found reconstruction.py at: {reconstruction_file}")
    
    try:
        # 파일 읽기
        with open(reconstruction_file, 'r') as f:
            content = f.read()
        
        # 이미 패치되었는지 확인
        if 'PYCOLMAP_API_FIX_PATCH' in content:
            print("✓ hloc reconstruction.py already patched")
            return True
        
        # image_names=를 image_list=로 교체
        if 'image_names=image_list or []' in content:
            # API 수정
            original_line = 'image_names=image_list or []'
            new_line = 'image_list=list(image_list or [])  # PYCOLMAP_API_FIX_PATCH'
            
            patched_content = content.replace(original_line, new_line)
            
            # database_path와 image_dir의 str 캐스팅도 추가
            patched_content = patched_content.replace(
                'pycolmap.import_images(\n            database_path,\n            image_dir,',
                'pycolmap.import_images(\n            str(database_path),  # PYCOLMAP_API_FIX_PATCH\n            str(image_dir),  # PYCOLMAP_API_FIX_PATCH'
            )
            
            # 파일 쓰기
            with open(reconstruction_file, 'w') as f:
                f.write(patched_content)
            
            print("✓ Applied pycolmap API fixes:")
            print("  - Changed image_names= to image_list=")
            print("  - Added str() casting for Path objects")
            return True
        else:
            print("⚠ Expected pattern not found in reconstruction.py")
            print("  File may have been updated or pattern changed")
            return False
            
    except Exception as e:
        print(f"ERROR patching reconstruction.py: {e}")
        return False


if __name__ == "__main__":
    print("=== Direct hloc reconstruction.py API fix ===")
    
    if patch_reconstruction_directly():
        print("✅ Direct reconstruction patch completed")
        sys.exit(0)
    else:
        print("❌ Direct reconstruction patch failed")
        sys.exit(1)