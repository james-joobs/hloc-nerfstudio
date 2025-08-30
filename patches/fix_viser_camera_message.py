#!/usr/bin/env python3
"""
viser CameraMessage 호환성 패치
nerfstudio와 viser 0.2.7 간의 메시지 타입 불일치 해결
"""

import sys
from pathlib import Path


def patch_viser_messages():
    """viser의 메시지 타입에 CameraMessage 별칭 추가"""
    try:
        # viser messages 모듈 찾기
        import viser.infra._messages as messages
        
        # ViewerCameraMessage를 CameraMessage로도 등록
        if hasattr(messages, 'ViewerCameraMessage'):
            # 메시지 레지스트리에 별칭 추가
            if hasattr(messages.Message, '_subclass_from_type_string'):
                registry = messages.Message._subclass_from_type_string()
                if 'ViewerCameraMessage' in registry and 'CameraMessage' not in registry:
                    registry['CameraMessage'] = registry['ViewerCameraMessage']
                    print("✓ Added CameraMessage alias to viser message registry")
                    return True
                elif 'CameraMessage' in registry:
                    print("  CameraMessage already registered")
                    return True
        
        print("⚠ Could not add CameraMessage alias - ViewerCameraMessage not found")
        return False
        
    except Exception as e:
        print(f"ERROR patching viser messages: {e}")
        return False


def patch_nerfstudio_imports():
    """nerfstudio의 CameraMessage import를 ViewerCameraMessage로 리다이렉트"""
    try:
        # nerfstudio viewer 모듈들 찾기
        nerfstudio_path = Path('/usr/local/lib/python3.10/dist-packages/nerfstudio')
        
        if not nerfstudio_path.exists():
            print(f"WARNING: nerfstudio not found at {nerfstudio_path}")
            return False
        
        # viewer_legacy 디렉토리의 viser/messages.py 수정
        legacy_messages = nerfstudio_path / 'viewer_legacy' / 'viser' / 'messages.py'
        if legacy_messages.exists():
            print(f"Patching: {legacy_messages}")
            
            with open(legacy_messages, 'r') as f:
                content = f.read()
            
            # CameraMessage 클래스가 없으면 ViewerCameraMessage 별칭 추가
            if 'class CameraMessage' not in content and 'CameraMessage =' not in content:
                # 파일 끝에 별칭 추가
                patch_code = """

# VISER_COMPAT_PATCH - Compatibility with viser 0.2.7
try:
    from viser.infra._messages import ViewerCameraMessage
    CameraMessage = ViewerCameraMessage
except ImportError:
    # Fallback to dataclass definition
    from dataclasses import dataclass
    from typing import Tuple, Optional
    
    @dataclass
    class CameraMessage:
        \"\"\"Camera message for viewer compatibility\"\"\"
        aspect: float
        render_height: int
        render_width: int
        fov: float
        matrix: Tuple[float, ...]
        camera_type: str = "perspective"
        is_moving: bool = False
        timestamp: Optional[float] = None
"""
                
                with open(legacy_messages, 'w') as f:
                    f.write(content + patch_code)
                
                print(f"✓ Patched {legacy_messages}")
                return True
            else:
                print(f"  CameraMessage already defined in {legacy_messages}")
                return True
        
        # 대체 방법: viewer 모듈에서 직접 import 수정
        viewer_files = [
            nerfstudio_path / 'viewer' / 'render_state_machine.py',
            nerfstudio_path / 'viewer' / 'viewer.py',
        ]
        
        patched_count = 0
        for viewer_file in viewer_files:
            if viewer_file.exists():
                with open(viewer_file, 'r') as f:
                    content = f.read()
                
                # CameraMessage import를 ViewerCameraMessage로 변경
                if 'from viser' in content and 'CameraMessage' in content:
                    modified = content.replace(
                        'from viser.infra._messages import CameraMessage',
                        'from viser.infra._messages import ViewerCameraMessage as CameraMessage'
                    )
                    
                    if modified != content:
                        with open(viewer_file, 'w') as f:
                            f.write(modified)
                        print(f"✓ Patched {viewer_file.name}")
                        patched_count += 1
        
        if patched_count > 0:
            print(f"Patched {patched_count} viewer files")
            return True
        
        return True
        
    except Exception as e:
        print(f"ERROR patching nerfstudio imports: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_startup_hook():
    """시작 시 자동으로 패치를 적용하는 훅 생성"""
    try:
        # sitecustomize.py에 패치 추가
        sitecustomize_path = Path('/usr/local/lib/python3.10/dist-packages/sitecustomize.py')
        
        patch_code = """
# VISER_COMPAT_PATCH - Auto-patch viser CameraMessage compatibility
try:
    import viser.infra._messages as messages
    if hasattr(messages, 'ViewerCameraMessage'):
        if hasattr(messages.Message, '_subclass_from_type_string'):
            registry = messages.Message._subclass_from_type_string()
            if 'ViewerCameraMessage' in registry and 'CameraMessage' not in registry:
                registry['CameraMessage'] = registry['ViewerCameraMessage']
except:
    pass
"""
        
        if sitecustomize_path.exists():
            with open(sitecustomize_path, 'r') as f:
                content = f.read()
            
            if 'VISER_COMPAT_PATCH' not in content:
                with open(sitecustomize_path, 'a') as f:
                    f.write(patch_code)
                print(f"✓ Added startup hook to {sitecustomize_path}")
        else:
            with open(sitecustomize_path, 'w') as f:
                f.write(patch_code)
            print(f"✓ Created {sitecustomize_path} with startup hook")
        
        return True
        
    except Exception as e:
        print(f"WARNING: Could not create startup hook: {e}")
        return False


if __name__ == "__main__":
    print("=== Fixing viser CameraMessage compatibility ===")
    
    # 1단계: viser 메시지 레지스트리 패치
    print("\nStep 1: Patching viser message registry...")
    viser_patched = patch_viser_messages()
    
    # 2단계: nerfstudio import 패치
    print("\nStep 2: Patching nerfstudio imports...")
    nerfstudio_patched = patch_nerfstudio_imports()
    
    # 3단계: 시작 훅 생성
    print("\nStep 3: Creating startup hook...")
    hook_created = create_startup_hook()
    
    # 검증
    print("\n=== Verifying patch ===")
    try:
        import viser.infra._messages as messages
        if hasattr(messages.Message, '_subclass_from_type_string'):
            registry = messages.Message._subclass_from_type_string()
            if 'CameraMessage' in registry:
                print("✅ CameraMessage is now registered in viser")
            else:
                print("❌ CameraMessage is still not registered")
    except Exception as e:
        print(f"Could not verify: {e}")
    
    if viser_patched or nerfstudio_patched or hook_created:
        print("\n✅ Compatibility patches applied")
        sys.exit(0)
    else:
        print("\n⚠ No patches were applied, but continuing anyway")
        sys.exit(0)