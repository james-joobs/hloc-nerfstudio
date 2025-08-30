#!/usr/bin/env python3
"""
통합 패치 적용 스크립트
모든 필요한 패치를 순서대로 적용
"""

import sys
import os
from pathlib import Path

# 패치 디렉터리를 Python path에 추가
patches_dir = Path(__file__).parent.parent / 'patches'
sys.path.insert(0, str(patches_dir))


def apply_all_patches():
    """모든 패치를 순서대로 적용"""
    print("=== Applying all compatibility patches ===")
    
    # pycolmap 관련 패치 비활성화 확인
    apply_pycolmap_patches = os.getenv('APPLY_PYCOLMAP_PATCHES', 'true').lower() == 'true'
    
    if not apply_pycolmap_patches:
        print("ℹ APPLY_PYCOLMAP_PATCHES=false, skipping pycolmap-dependent patches")
        print("→ Using COLMAP binary fallback mode")
        return True  # 성공으로 간주
    
    patches = [
        ("LightGlue Offline", "lightglue_offline"),
        ("hloc parsers fallback", "hloc_parsers_fallback"),  # 기존 작동하던 핵심 패치  
        ("pycolmap import fallback SAFE", "pycolmap_import_fallback_safe"),  # 안전한 버전 - 중복 패치 방지
        ("hloc reconstruction API fix", "hloc_reconstruction_api_fix"),  # pycolmap 0.6.1 API 호환성
        ("hloc frames.bin safe move", "hloc_frames_bin_fix"),  # frames.bin/rigs.bin 이동 에러 방지
    ]
    
    success_count = 0
    total_count = len(patches)
    
    for patch_name, patch_module in patches:
        print(f"\n--- Applying {patch_name} patch ---")
        try:
            # 동적으로 패치 모듈 import
            patch = __import__(patch_module)
            
            # 메인 함수 실행
            if hasattr(patch, 'main'):
                success = patch.main()
            else:
                # 모듈을 직접 실행
                import subprocess
                result = subprocess.run([
                    sys.executable, 
                    str(patches_dir / f"{patch_module}.py")
                ], capture_output=True, text=True)
                success = result.returncode == 0
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
            
            if success:
                print(f"✅ {patch_name} patch applied successfully")
                success_count += 1
            else:
                print(f"❌ {patch_name} patch failed")
                
        except Exception as e:
            print(f"ERROR applying {patch_name} patch: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== Patch Summary ===")
    print(f"Successfully applied: {success_count}/{total_count} patches")
    
    if success_count == total_count:
        print("✅ All patches applied successfully!")
        return True
    elif success_count > 0:
        print(f"⚠ Partial success: {success_count}/{total_count} patches applied")
        print("→ Continuing with available functionality")
        return True  # 일부 패치라도 성공했으면 계속 진행
    else:
        print("❌ No patches applied successfully!")
        print("→ Continuing with COLMAP binary fallback only")
        return True  # 패치 실패해도 COLMAP 바이너리는 사용 가능


if __name__ == "__main__":
    success = apply_all_patches()
    sys.exit(0 if success else 1)