#!/usr/bin/env python3
"""
PyMeshLab import 우회 패치
ns-export에서 PyMeshLab 의존성을 우회하여 기본 기능은 동작하도록 함
"""

import os
import sys
from pathlib import Path


def patch_exporter_utils():
    """nerfstudio exporter_utils.py에서 PyMeshLab import 우회"""
    try:
        # Find nerfstudio installation path
        import nerfstudio
        ns_path = Path(nerfstudio.__file__).parent
        exporter_utils_file = ns_path / "exporter" / "exporter_utils.py"
        
        if not exporter_utils_file.exists():
            print(f"WARNING: {exporter_utils_file} not found")
            return False
            
        print(f"Patching: {exporter_utils_file}")
        
        with open(exporter_utils_file, 'r') as f:
            content = f.read()
        
        # PyMeshLab import를 try-except로 감싸서 실패시에도 계속 진행
        if 'import pymeshlab' in content and 'try:' not in content.split('import pymeshlab')[0][-50:]:
            # Find the pymeshlab import line
            lines = content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                if 'import pymeshlab' in line and not line.strip().startswith('#'):
                    # Replace with conditional import
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(' ' * indent + '# PyMeshLab import with fallback')
                    new_lines.append(' ' * indent + 'try:')
                    new_lines.append(' ' * (indent + 4) + line.strip())
                    new_lines.append(' ' * indent + 'except ImportError:')
                    new_lines.append(' ' * (indent + 4) + 'print("WARNING: PyMeshLab not available, mesh export will be limited")')
                    new_lines.append(' ' * (indent + 4) + 'pymeshlab = None')
                else:
                    new_lines.append(line)
            
            patched_content = '\n'.join(new_lines)
            
            with open(exporter_utils_file, 'w') as f:
                f.write(patched_content)
            
            print(f"✓ PyMeshLab import patched in {exporter_utils_file.name}")
            return True
        else:
            print(f"  Already patched or no pymeshlab import found")
            return True
            
    except Exception as e:
        print(f"ERROR patching exporter_utils: {e}")
        return False


def patch_texture_utils():
    """texture_utils.py 패치"""
    try:
        import nerfstudio
        ns_path = Path(nerfstudio.__file__).parent
        texture_utils_file = ns_path / "exporter" / "texture_utils.py"
        
        if not texture_utils_file.exists():
            print(f"WARNING: {texture_utils_file} not found")
            return True  # 파일이 없으면 성공으로 간주
            
        print(f"Patching: {texture_utils_file}")
        
        with open(texture_utils_file, 'r') as f:
            content = f.read()
        
        # exporter_utils import도 안전하게 처리
        if 'from nerfstudio.exporter.exporter_utils import Mesh' in content:
            content = content.replace(
                'from nerfstudio.exporter.exporter_utils import Mesh',
                '''try:
    from nerfstudio.exporter.exporter_utils import Mesh
except ImportError as e:
    print(f"WARNING: Could not import Mesh from exporter_utils: {e}")
    # Mesh 클래스 모킹
    class Mesh:
        def __init__(self, *args, **kwargs):
            pass'''
            )
            
            with open(texture_utils_file, 'w') as f:
                f.write(content)
            
            print(f"✓ Mesh import patched in {texture_utils_file.name}")
        
        return True
        
    except Exception as e:
        print(f"ERROR patching texture_utils: {e}")
        return False


def patch_tsdf_utils():
    """tsdf_utils.py에서 PyMeshLab import 우회"""
    try:
        import nerfstudio
        ns_path = Path(nerfstudio.__file__).parent
        tsdf_utils_file = ns_path / "exporter" / "tsdf_utils.py"
        
        if not tsdf_utils_file.exists():
            print(f"WARNING: {tsdf_utils_file} not found")
            return True
            
        print(f"Patching: {tsdf_utils_file}")
        
        with open(tsdf_utils_file, 'r') as f:
            content = f.read()
        
        # PyMeshLab import를 try-except로 감싸기
        if 'import pymeshlab' in content and 'try:' not in content.split('import pymeshlab')[0][-50:]:
            content = content.replace(
                'import pymeshlab',
                '''try:
    import pymeshlab
except ImportError:
    print("WARNING: PyMeshLab not available, TSDF mesh export will be disabled")
    pymeshlab = None'''
            )
            
            with open(tsdf_utils_file, 'w') as f:
                f.write(content)
            
            print(f"✓ PyMeshLab import patched in {tsdf_utils_file.name}")
        
        return True
        
    except Exception as e:
        print(f"ERROR patching tsdf_utils: {e}")
        return False


if __name__ == "__main__":
    print("=== PyMeshLab import bypass patch ===")
    
    success = True
    
    print("\nStep 1: Patching exporter_utils.py...")
    success &= patch_exporter_utils()
    
    print("\nStep 2: Patching texture_utils.py...")
    success &= patch_texture_utils()
    
    print("\nStep 3: Patching tsdf_utils.py...")
    success &= patch_tsdf_utils()
    
    if success:
        print("\n✅ PyMeshLab bypass patches applied successfully")
        print("Note: Mesh export functionality will be limited without PyMeshLab")
        sys.exit(0)
    else:
        print("\n❌ Some patches failed")
        sys.exit(1)