#!/usr/bin/env python3
"""
pycolmap import fallback 패치 - 안전한 버전
hloc의 기존 try-except-else 구조를 고려하여 적절히 패치
"""

import sys
import os
import re
from pathlib import Path


def patch_hloc_init():
    """hloc/__init__.py의 pycolmap import를 더 안전하게 수정"""
    try:
        init_file = Path('/usr/local/lib/python3.10/dist-packages/hloc/__init__.py')
        
        if not init_file.exists():
            # 대체 경로 시도
            alt_paths = [
                Path('/usr/local/lib/python3.10/site-packages/hloc/__init__.py'),
                Path('/opt/conda/lib/python3.10/site-packages/hloc/__init__.py'),
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    init_file = alt_path
                    break
            else:
                print(f"ERROR: hloc/__init__.py not found")
                return False
        
        print(f"Patching: {init_file}")
        
        with open(init_file, 'r') as f:
            lines = f.readlines()
        
        # 이미 패치되었는지 확인
        content = ''.join(lines)
        if 'PYCOLMAP_SAFE_IMPORT' in content:
            print(f"  Already patched: {init_file}")
            return True
        
        # hloc의 기존 try-except-else 구조를 보존하면서 안전하게 수정
        modified_lines = []
        i = 0
        patched = False
        
        while i < len(lines):
            line = lines[i]
            
            # try 블록 찾기
            if line.strip().startswith('try:') and not patched:
                # try 블록부터 else까지 모두 찾기
                try_block_start = i
                modified_lines.append(line)
                i += 1
                
                # import pycolmap 라인 찾기
                while i < len(lines) and not lines[i].strip().startswith('except'):
                    modified_lines.append(lines[i])
                    if 'import pycolmap' in lines[i]:
                        import_line_idx = len(modified_lines) - 1
                    i += 1
                
                # except 블록 처리
                if i < len(lines) and lines[i].strip().startswith('except'):
                    # except ImportError를 더 포괄적으로 수정
                    if 'ImportError' in lines[i]:
                        modified_lines.append('except (ImportError, RuntimeError) as e:\n')
                        modified_lines.append('    # PYCOLMAP_SAFE_IMPORT - Enhanced error handling\n')
                        i += 1
                        
                        # 기존 except 블록 내용 건너뛰기
                        indent_level = len(lines[i]) - len(lines[i].lstrip())
                        while i < len(lines) and (lines[i].strip() == '' or 
                                                  (lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) > 0)):
                            if 'logger.warning' in lines[i]:
                                modified_lines.append("    logger.warning(f'pycolmap import failed ({e}), using COLMAP binary fallback')\n")
                                modified_lines.append("    pycolmap = None\n")
                                modified_lines.append("    _pycolmap_available = False\n")
                            i += 1
                            if i < len(lines) and lines[i].strip().startswith('else:'):
                                break
                    else:
                        modified_lines.append(lines[i])
                        i += 1
                
                # else 블록 처리
                if i < len(lines) and lines[i].strip().startswith('else:'):
                    modified_lines.append(lines[i])
                    i += 1
                    # else 블록 첫 줄에 _pycolmap_available = True 추가
                    if i < len(lines):
                        indent = '    '  # else 블록 내부 들여쓰기
                        modified_lines.append(f'{indent}_pycolmap_available = True\n')
                        modified_lines.append(f'{indent}# PYCOLMAP_SAFE_IMPORT - pycolmap successfully imported\n')
                
                patched = True
            else:
                modified_lines.append(line)
                i += 1
        
        if patched:
            with open(init_file, 'w') as f:
                f.writelines(modified_lines)
            print(f"✓ Patched: {init_file}")
            return True
        else:
            print(f"  No suitable try-except block found in: {init_file}")
            return False
            
    except Exception as e:
        print(f"ERROR patching hloc/__init__.py: {e}")
        import traceback
        traceback.print_exc()
        return False


def patch_hloc_parsers():
    """hloc/utils/parsers.py의 pycolmap import 수정"""
    try:
        parsers_file = Path('/usr/local/lib/python3.10/dist-packages/hloc/utils/parsers.py')
        
        if not parsers_file.exists():
            # 대체 경로 시도
            alt_paths = [
                Path('/usr/local/lib/python3.10/site-packages/hloc/utils/parsers.py'),
                Path('/opt/conda/lib/python3.10/site-packages/hloc/utils/parsers.py'),
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    parsers_file = alt_path
                    break
            else:
                print(f"WARNING: hloc/utils/parsers.py not found")
                return True  # 파일이 없으면 성공으로 간주
        
        print(f"Patching: {parsers_file}")
        
        with open(parsers_file, 'r') as f:
            content = f.read()
        
        # 이미 패치되었는지 확인
        if 'PYCOLMAP_SAFE_IMPORT' in content:
            print(f"  Already patched: {parsers_file}")
            return True
        
        # 단순 import pycolmap을 안전한 버전으로 교체
        if 'import pycolmap' in content:
            # parsers.py는 단순 import일 가능성이 높음
            modified_content = re.sub(
                r'^(\s*)import pycolmap\s*$',
                r'''\1# PYCOLMAP_SAFE_IMPORT
\1try:
\1    import pycolmap
\1    _pycolmap_available = True
\1except (ImportError, RuntimeError) as e:
\1    print(f"WARNING: pycolmap import failed ({e}) in parsers.py")
\1    pycolmap = None
\1    _pycolmap_available = False''',
                content,
                flags=re.MULTILINE
            )
            
            if modified_content != content:
                with open(parsers_file, 'w') as f:
                    f.write(modified_content)
                print(f"✓ Patched: {parsers_file}")
                return True
        
        print(f"  No pycolmap import found in: {parsers_file}")
        return True
        
    except Exception as e:
        print(f"ERROR patching hloc/utils/parsers.py: {e}")
        return False


def patch_other_files():
    """hloc의 다른 파일들에서 pycolmap import를 안전하게 처리"""
    try:
        hloc_path = Path('/usr/local/lib/python3.10/dist-packages/hloc')
        if not hloc_path.exists():
            hloc_path = Path('/usr/local/lib/python3.10/site-packages/hloc')
            if not hloc_path.exists():
                print("WARNING: hloc package not found")
                return True
        
        # __init__.py와 parsers.py는 이미 처리했으므로 제외
        exclude_files = {'__init__.py', 'parsers.py'}
        
        patched_count = 0
        for py_file in hloc_path.rglob("*.py"):
            if py_file.name in exclude_files:
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # pycolmap을 import하는 파일만 처리
                if re.search(r'^\s*import pycolmap\s*$', content, re.MULTILINE):
                    # 이미 패치되었는지 확인
                    if 'PYCOLMAP_SAFE_IMPORT' in content:
                        continue
                    
                    modified_content = re.sub(
                        r'^(\s*)import pycolmap\s*$',
                        r'''\1# PYCOLMAP_SAFE_IMPORT
\1try:
\1    import pycolmap
\1except (ImportError, RuntimeError):
\1    pycolmap = None''',
                        content,
                        flags=re.MULTILINE
                    )
                    
                    if modified_content != content:
                        with open(py_file, 'w') as f:
                            f.write(modified_content)
                        print(f"✓ Patched: {py_file.relative_to(hloc_path)}")
                        patched_count += 1
                        
            except Exception as e:
                print(f"Failed to patch {py_file}: {e}")
        
        if patched_count > 0:
            print(f"Patched {patched_count} additional files")
        
        return True
        
    except Exception as e:
        print(f"ERROR patching other files: {e}")
        return False


def verify_syntax():
    """패치된 파일들의 Python 구문 검증"""
    try:
        hloc_path = Path('/usr/local/lib/python3.10/dist-packages/hloc')
        if not hloc_path.exists():
            hloc_path = Path('/usr/local/lib/python3.10/site-packages/hloc')
            if not hloc_path.exists():
                print("WARNING: hloc package not found for verification")
                return True
        
        target_files = [
            hloc_path / '__init__.py',
            hloc_path / 'utils' / 'parsers.py',
        ]
        
        print("\n=== Verifying Python syntax ===")
        all_valid = True
        
        for py_file in target_files:
            if not py_file.exists():
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Python 구문 검증
                compile(content, str(py_file), 'exec')
                print(f"✓ Valid syntax: {py_file.relative_to(hloc_path)}")
                
            except SyntaxError as e:
                print(f"✗ Syntax error in {py_file.relative_to(hloc_path)}:")
                print(f"  Line {e.lineno}: {e.msg}")
                print(f"  Text: {e.text}")
                all_valid = False
            except Exception as e:
                print(f"✗ Error checking {py_file}: {e}")
                all_valid = False
                
        return all_valid
        
    except Exception as e:
        print(f"ERROR: verification failed: {e}")
        return False


if __name__ == "__main__":
    print("=== Safe pycolmap import fallback patch ===")
    
    # 1단계: hloc/__init__.py 패치
    print("\nStep 1: Patching hloc/__init__.py...")
    init_success = patch_hloc_init()
    
    # 2단계: hloc/utils/parsers.py 패치
    print("\nStep 2: Patching hloc/utils/parsers.py...")
    parsers_success = patch_hloc_parsers()
    
    # 3단계: 다른 파일들 패치
    print("\nStep 3: Patching other files...")
    others_success = patch_other_files()
    
    # 4단계: 구문 검증
    print("\nStep 4: Verifying syntax...")
    syntax_valid = verify_syntax()
    
    if init_success and parsers_success and others_success and syntax_valid:
        print("\n✅ All patches applied successfully with valid syntax")
        sys.exit(0)
    else:
        print("\n⚠ Some patches failed or have syntax errors, but continuing...")
        sys.exit(0)  # 실패해도 빌드는 계속 진행