#!/usr/bin/env python3
"""
hloc 구문 오류 수정 스크립트
도커 빌드 시 hloc의 잘못된 pycolmap import를 수정
"""

import sys
import os
from pathlib import Path


def fix_hloc_init():
    """hloc/__init__.py의 구문 오류 수정"""
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
    
    print(f"Fixing: {init_file}")
    
    try:
        with open(init_file, 'r') as f:
            lines = f.readlines()
        
        # 수정이 필요한 부분 찾기
        new_lines = []
        skip_lines = False
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 주석처리된 try 제거
            if line.strip() == '#try:':
                i += 1
                continue
            
            # PYCOLMAP_SAFE_IMPORT 패치 발견
            if 'PYCOLMAP_SAFE_IMPORT' in line:
                # 패치 블록 시작
                new_lines.append(line)  # PYCOLMAP_SAFE_IMPORT 주석
                i += 1
                
                # try 블록 추가 (except까지 포함)
                while i < len(lines) and '_pycolmap_available = False' not in lines[i]:
                    new_lines.append(lines[i])
                    i += 1
                
                # _pycolmap_available = False 라인도 추가
                if i < len(lines):
                    new_lines.append(lines[i])
                    i += 1
                
                # 중복된 except 블록들 건너뛰기
                while i < len(lines) and ('except' in lines[i] or 'logger.warning' in lines[i] or lines[i].strip() == 'else:'):
                    i += 1
                
                # 다음 실제 코드까지 건너뛰기
                while i < len(lines) and (lines[i].strip() == '' or lines[i].strip().startswith('#') or 'min_version' in lines[i] or not lines[i].strip().startswith('from')):
                    i += 1
                
                continue
            
            new_lines.append(line)
            i += 1
        
        # 파일 다시 쓰기
        with open(init_file, 'w') as f:
            f.writelines(new_lines)
        
        print(f"✓ Fixed {init_file}")
        return True
        
    except Exception as e:
        print(f"ERROR fixing {init_file}: {e}")
        return False


def fix_hloc_parsers():
    """hloc/utils/parsers.py의 구문 오류 수정"""
    parsers_file = Path('/usr/local/lib/python3.10/dist-packages/hloc/utils/parsers.py')
    
    if not parsers_file.exists():
        print(f"WARNING: {parsers_file} not found")
        return True  # 파일이 없으면 성공으로 간주
    
    print(f"Fixing: {parsers_file}")
    
    try:
        with open(parsers_file, 'r') as f:
            content = f.read()
        
        # 잘못된 부분 수정
        # pycolmap이 None인데 __version__ 접근하는 부분 제거
        fixed_content = content
        
        # 패턴 1: except 블록 내의 잘못된 print 문 제거
        import re
        fixed_content = re.sub(
            r'pycolmap = None\n.*?_pycolmap_available = False\n.*?# pycolmap.*?\n.*?print\(f"INFO:.*?\"\)',
            'pycolmap = None\n    _pycolmap_available = False',
            fixed_content,
            flags=re.DOTALL
        )
        
        with open(parsers_file, 'w') as f:
            f.write(fixed_content)
        
        print(f"✓ Fixed {parsers_file}")
        return True
        
    except Exception as e:
        print(f"ERROR fixing {parsers_file}: {e}")
        return False


def verify_syntax():
    """수정된 파일들의 Python 구문 검증"""
    files_to_check = [
        Path('/usr/local/lib/python3.10/dist-packages/hloc/__init__.py'),
        Path('/usr/local/lib/python3.10/dist-packages/hloc/utils/parsers.py'),
    ]
    
    print("\n=== Verifying Python syntax ===")
    all_valid = True
    
    for py_file in files_to_check:
        if not py_file.exists():
            continue
            
        try:
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Python 구문 검증
            compile(content, str(py_file), 'exec')
            print(f"✓ Valid syntax: {py_file.name}")
            
        except SyntaxError as e:
            print(f"✗ Syntax error in {py_file.name}:")
            print(f"  Line {e.lineno}: {e.msg}")
            all_valid = False
        except Exception as e:
            print(f"✗ Error checking {py_file}: {e}")
            all_valid = False
            
    return all_valid


if __name__ == "__main__":
    print("=== Fixing hloc syntax errors ===")
    
    # 1단계: __init__.py 수정
    print("\nStep 1: Fixing __init__.py...")
    init_fixed = fix_hloc_init()
    
    # 2단계: parsers.py 수정  
    print("\nStep 2: Fixing parsers.py...")
    parsers_fixed = fix_hloc_parsers()
    
    # 3단계: 구문 검증
    print("\nStep 3: Verifying syntax...")
    if verify_syntax():
        print("\n✅ All files have valid Python syntax")
        sys.exit(0)
    else:
        print("\n❌ Some files still have syntax errors")
        sys.exit(1)