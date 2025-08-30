#!/usr/bin/env python3
"""
hloc reconstruction.py frames.bin/rigs.bin 이동 에러 수정
파일 존재 여부 확인 후에만 이동하도록 패치
"""

import sys
import re
from pathlib import Path


def patch_hloc_frames_bin_move():
    """hloc reconstruction.py의 frames.bin/rigs.bin 이동 로직을 안전하게 수정"""
    
    # 가능한 hloc reconstruction.py 경로들
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
        if 'FRAMES_BIN_SAFE_MOVE' in content:
            print("✓ hloc reconstruction.py already patched for frames.bin/rigs.bin")
            return True
        
        # 문제가 되는 패턴 찾기
        # shutil.move 무조건 실행하는 부분을 파일 존재 확인 후 실행으로 변경
        problem_pattern = r'(\s+)shutil\.move\(str\(models_path / str\(largest_index\) / filename\), str\(sfm_dir\)\)'
        
        # 새로운 안전한 코드
        safe_move_code = r'''\1# FRAMES_BIN_SAFE_MOVE - 파일 존재 확인 후 이동
\1src_file = models_path / str(largest_index) / filename
\1if src_file.exists():
\1    shutil.move(str(src_file), str(sfm_dir))
\1else:
\1    print(f"INFO: {filename} not found, skipping move (normal for image-only imports)")'''
        
        # 패턴 교체
        patched_content = re.sub(problem_pattern, safe_move_code, content)
        
        if patched_content != content:
            # 파일 쓰기
            with open(reconstruction_file, 'w') as f:
                f.write(patched_content)
            
            print("✓ Applied frames.bin/rigs.bin safe move patch:")
            print("  - Added file existence check before shutil.move()")
            print("  - Prevents FileNotFoundError for image-only imports")
            return True
        else:
            print("⚠ Pattern not found - reconstruction.py may have been updated")
            return False
            
    except Exception as e:
        print(f"ERROR patching reconstruction.py: {e}")
        return False


if __name__ == "__main__":
    print("=== hloc frames.bin/rigs.bin safe move patch ===")
    
    if patch_hloc_frames_bin_move():
        print("✅ frames.bin/rigs.bin move patch completed")
        sys.exit(0)
    else:
        print("❌ frames.bin/rigs.bin move patch failed")
        sys.exit(1)