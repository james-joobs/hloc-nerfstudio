#!/usr/bin/env python3
"""
COLMAP Binary Mode 설정 스크립트
pycolmap C++ 백엔드 문제를 우회하여 COLMAP 바이너리만 사용
"""

import sys
import os
import shutil
from pathlib import Path


def create_pycolmap_stub():
    """최소한의 pycolmap 호환성 모듈 생성"""
    print("Creating pycolmap compatibility stub...")
    
    try:
        # 기존 pycolmap 확인
        try:
            import pycolmap
            pycolmap_path = Path(pycolmap.__file__).parent
            print(f"Found existing pycolmap at: {pycolmap_path}")
            
            # _core 모듈 문제가 있는지 테스트
            try:
                import pycolmap._core
                print("✅ pycolmap._core works fine, no stub needed")
                return True
            except Exception as e:
                print(f"⚠ pycolmap._core failed: {e}")
                print("Creating compatibility stub...")
                
        except ImportError:
            print("pycolmap not found, creating minimal version")
            pycolmap_path = Path("/usr/local/lib/python3.10/site-packages/pycolmap")
        
        # 호환성 stub 내용
        stub_content = '''"""
pycolmap compatibility stub for COLMAP binary mode
This module provides minimal compatibility when pycolmap C++ backend fails
"""

import os
import subprocess
from enum import Enum
from pathlib import Path

__version__ = "3.12.4-stub"

# Camera models enum
class CameraMode(Enum):
    AUTO = 0
    SINGLE = 1
    PER_FOLDER = 2
    PER_IMAGE = 3

# Options classes
class ImageReaderOptions:
    def __init__(self):
        self.camera_model = "SIMPLE_PINHOLE"
        self.single_camera = False
        self.single_camera_per_folder = False
        self.existing_camera_id = -1

class SiftExtractionOptions:
    def __init__(self):
        self.max_image_size = 3200
        self.max_num_features = 8192
        self.first_octave = -1
        self.num_octaves = 4

class SiftMatchingOptions:
    def __init__(self):
        self.max_ratio = 0.8
        self.max_distance = 0.7
        self.cross_check = True
        self.max_error = 4.0

# COLMAP binary wrapper functions
def _run_colmap_command(cmd, check=True):
    """Run COLMAP binary command"""
    colmap_bin = os.environ.get('COLMAP_EXE_PATH', '/usr/local/bin/colmap')
    if not os.path.exists(colmap_bin):
        raise RuntimeError(f"COLMAP binary not found at {colmap_bin}")
    
    full_cmd = [colmap_bin] + cmd if isinstance(cmd, list) else f"{colmap_bin} {cmd}"
    
    try:
        result = subprocess.run(full_cmd, shell=isinstance(full_cmd, str), 
                              capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"COLMAP command failed: {e}")

def import_images(database_path, image_path, camera_mode=CameraMode.AUTO, 
                 image_list=None, options=None):
    """Import images using COLMAP binary"""
    if image_list is None:
        image_list = []
    if options is None:
        options = ImageReaderOptions()
    
    print(f"Importing images via COLMAP binary: {database_path} <- {image_path}")
    
    cmd = [
        "feature_extractor",
        "--database_path", str(database_path),
        "--image_path", str(image_path),
        "--ImageReader.camera_model", options.camera_model,
    ]
    
    if camera_mode == CameraMode.SINGLE:
        cmd.extend(["--ImageReader.single_camera", "1"])
    
    return _run_colmap_command(cmd)

def extract_features(database_path, image_path, options=None):
    """Extract features using COLMAP binary"""
    if options is None:
        options = SiftExtractionOptions()
    
    print(f"Extracting features via COLMAP binary")
    
    cmd = [
        "feature_extractor",
        "--database_path", str(database_path),
        "--image_path", str(image_path),
        "--SiftExtraction.max_image_size", str(options.max_image_size),
        "--SiftExtraction.max_num_features", str(options.max_num_features),
    ]
    
    return _run_colmap_command(cmd)

def match_features(database_path, options=None):
    """Match features using COLMAP binary"""
    if options is None:
        options = SiftMatchingOptions()
    
    print(f"Matching features via COLMAP binary")
    
    cmd = [
        "exhaustive_matcher",
        "--database_path", str(database_path),
        "--SiftMatching.max_ratio", str(options.max_ratio),
        "--SiftMatching.max_distance", str(options.max_distance),
    ]
    
    return _run_colmap_command(cmd)

# C++ backend stub (always fails gracefully)
class _CoreStub:
    """Stub for pycolmap._core that always raises appropriate errors"""
    
    def __getattr__(self, name):
        raise RuntimeError(
            f"pycolmap C++ backend not available. "
            f"Function '{name}' requires COLMAP binary implementation."
        )

# Install the stub
import sys
sys.modules[__name__ + '._core'] = _CoreStub()

print("🔧 pycolmap running in COLMAP binary compatibility mode")
'''
        
        # 디렉터리 생성
        pycolmap_path.mkdir(parents=True, exist_ok=True)
        
        # __init__.py 파일 생성/교체
        init_file = pycolmap_path / "__init__.py"
        with open(init_file, 'w') as f:
            f.write(stub_content)
        
        print(f"✅ pycolmap stub created at: {init_file}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create pycolmap stub: {e}")
        return False


def configure_environment():
    """COLMAP 바이너리 모드를 위한 환경 설정"""
    print("Configuring environment for COLMAP binary mode...")
    
    env_vars = {
        'COLMAP_EXE_PATH': '/usr/local/bin/colmap',
        'HLOC_COLMAP_PATH': '/usr/local/bin/colmap', 
        'HLOC_USE_PYCOLMAP': 'false',
        'COLMAP_BINARY_PATH': '/usr/local/bin/colmap',
    }
    
    # 환경변수 설정 스크립트 생성
    env_script = Path('/etc/environment.d/colmap-binary-mode.conf')
    env_script.parent.mkdir(exist_ok=True, parents=True)
    
    try:
        with open(env_script, 'w') as f:
            for key, value in env_vars.items():
                f.write(f'{key}={value}\n')
                os.environ[key] = value  # 현재 세션에도 적용
        
        print(f"✅ Environment configured: {env_script}")
        return True
        
    except Exception as e:
        print(f"⚠ Could not write environment file: {e}")
        # 현재 세션에만 적용
        for key, value in env_vars.items():
            os.environ[key] = value
        print("✅ Environment configured for current session")
        return True


def test_colmap_binary():
    """COLMAP 바이너리 동작 테스트"""
    print("Testing COLMAP binary functionality...")
    
    colmap_bin = os.environ.get('COLMAP_EXE_PATH', '/usr/local/bin/colmap')
    
    if not os.path.exists(colmap_bin):
        print(f"❌ COLMAP binary not found: {colmap_bin}")
        return False
    
    try:
        result = subprocess.run([colmap_bin, '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # 버전 정보 추출
            version_result = subprocess.run([colmap_bin, '-h'], 
                                          capture_output=True, text=True, timeout=5)
            for line in version_result.stdout.split('\n')[:3]:
                if 'COLMAP' in line:
                    print(f"✅ {line}")
                    break
            return True
        else:
            print(f"❌ COLMAP binary test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ COLMAP binary test error: {e}")
        return False


def main():
    """메인 설정 함수"""
    print("🔧 Setting up COLMAP Binary Mode")
    print("=" * 40)
    
    success = True
    success &= create_pycolmap_stub()
    success &= configure_environment()
    success &= test_colmap_binary()
    
    if success:
        print("\n✅ COLMAP Binary Mode setup completed successfully!")
        print("pycolmap C++ backend issues have been bypassed.")
    else:
        print("\n❌ Some setup steps failed!")
        
    return success


if __name__ == "__main__":
    import subprocess
    sys.exit(0 if main() else 1)