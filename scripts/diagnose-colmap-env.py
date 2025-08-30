#!/usr/bin/env python3
"""
COLMAP/pycolmap 환경 진단 스크립트
ABI 호환성 문제의 근본 원인을 분석
"""

import sys
import subprocess
import importlib.util
from pathlib import Path


def run_command(cmd):
    """명령어 실행 및 결과 반환"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)


def check_system_colmap():
    """시스템 COLMAP 정보 확인"""
    print("=== System COLMAP Information ===")
    
    # COLMAP 바이너리 확인
    ret, stdout, stderr = run_command("which colmap")
    if ret == 0:
        print(f"COLMAP binary: {stdout}")
        
        # 버전 확인
        ret, stdout, stderr = run_command("colmap -h 2>&1 | head -3")
        if ret == 0:
            for line in stdout.split('\n'):
                if 'COLMAP' in line:
                    print(f"Version: {line}")
                    break
    else:
        print("❌ COLMAP binary not found")
    
    # 라이브러리 경로 확인
    ret, stdout, stderr = run_command("ldconfig -p | grep -E '(colmap|ceres)'")
    if ret == 0 and stdout:
        print("System libraries:")
        for line in stdout.split('\n'):
            print(f"  {line}")


def check_ceres_solver():
    """Ceres Solver 정보 확인"""
    print("\n=== Ceres Solver Information ===")
    
    # pkg-config로 Ceres 정보 확인
    ret, stdout, stderr = run_command("pkg-config --modversion ceres")
    if ret == 0:
        print(f"Ceres version (pkg-config): {stdout}")
    else:
        print("⚠ Ceres not found via pkg-config")
    
    # 헤더 파일 확인
    ceres_headers = [
        "/usr/local/include/ceres/ceres.h",
        "/usr/include/ceres/ceres.h"
    ]
    
    for header in ceres_headers:
        if Path(header).exists():
            print(f"✓ Ceres headers found: {header}")
            
            # Manifold 클래스 확인
            ret, stdout, stderr = run_command(f"grep -n 'class.*Manifold' {header} || true")
            if stdout:
                print(f"  Manifold class definition found")
            else:
                # 다른 헤더에서 찾기
                ret, stdout, stderr = run_command(f"find /usr/local/include /usr/include -name '*.h' -exec grep -l 'class.*Manifold' {{}} \\; 2>/dev/null | head -3")
                if stdout:
                    print(f"  Manifold found in: {stdout}")
                else:
                    print("  ⚠ Manifold class not found")
            break
    else:
        print("❌ Ceres headers not found")


def check_pycolmap():
    """pycolmap 상세 정보 확인"""
    print("\n=== pycolmap Information ===")
    
    try:
        import pycolmap
        print(f"pycolmap version: {pycolmap.__version__}")
        print(f"pycolmap location: {pycolmap.__file__}")
        
        # pycolmap 빌드 정보 확인
        if hasattr(pycolmap, '__build_info__'):
            print(f"Build info: {pycolmap.__build_info__}")
        
        # _core 모듈 시도
        try:
            print("Attempting to import pycolmap._core...")
            import pycolmap._core
            print("✅ pycolmap._core imported successfully")
            
            # _core 모듈 정보
            if hasattr(pycolmap._core, '__version__'):
                print(f"_core version: {pycolmap._core.__version__}")
                
        except ImportError as e:
            print(f"❌ pycolmap._core import failed: {e}")
            
            # 에러 메시지 분석
            error_msg = str(e)
            if "PositiveExponentialManifold" in error_msg:
                print("  → ABI compatibility issue with Ceres Solver")
            if "ceres::Manifold" in error_msg:
                print("  → Ceres Manifold class not found in current environment")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            
    except ImportError:
        print("❌ pycolmap not installed")


def check_library_dependencies():
    """라이브러리 의존성 확인"""
    print("\n=== Library Dependencies ===")
    
    # pycolmap _core.so 의존성 확인
    try:
        import pycolmap
        pycolmap_path = Path(pycolmap.__file__).parent
        
        # _core.so 파일 찾기
        core_files = list(pycolmap_path.glob("**/_core*.so"))
        if not core_files:
            core_files = list(pycolmap_path.glob("**/*core*.so"))
            
        for core_file in core_files[:3]:  # 최대 3개만 확인
            print(f"Checking dependencies of: {core_file}")
            ret, stdout, stderr = run_command(f"ldd {core_file} 2>/dev/null | grep -E '(ceres|colmap)' || true")
            if stdout:
                for line in stdout.split('\n'):
                    print(f"  {line}")
            else:
                print("  No ceres/colmap dependencies found")
                
    except Exception as e:
        print(f"⚠ Could not check dependencies: {e}")


def suggest_solutions():
    """해결책 제안"""
    print("\n=== Suggested Solutions ===")
    
    solutions = [
        "1. Use COLMAP binary only (disable pycolmap C++ backend)",
        "2. Build pycolmap from source against current Ceres installation",
        "3. Use compatible pre-built pycolmap version",
        "4. Update system Ceres to match pycolmap requirements"
    ]
    
    for solution in solutions:
        print(solution)
    
    print("\nRecommended approach:")
    print("→ Disable pycolmap C++ backend and use COLMAP 3.12.4 binary only")
    print("→ This avoids ABI compatibility issues while maintaining functionality")


def main():
    """메인 진단 함수"""
    print("🔍 COLMAP/pycolmap Environment Diagnosis")
    print("=" * 50)
    
    check_system_colmap()
    check_ceres_solver()
    check_pycolmap()
    check_library_dependencies()
    suggest_solutions()
    
    print("\n✅ Diagnosis completed")


if __name__ == "__main__":
    main()