#!/usr/bin/env python3
"""
LightGlue 오프라인 패치 스크립트
네트워크 연결 없이 사전 다운로드된 모델을 사용하도록 패치
"""

import sys
import shutil
from pathlib import Path


def patch_lightglue():
    """LightGlue 라이브러리를 오프라인 모드로 패치"""
    try:
        import lightglue
        lightglue_path = Path(lightglue.__file__).parent
        lightglue_file = lightglue_path / 'lightglue.py'
        
        print(f"Patching LightGlue at: {lightglue_file}")
        
        # 백업 생성
        backup_file = lightglue_path / 'lightglue.py.backup'
        if not backup_file.exists():
            shutil.copy(lightglue_file, backup_file)
            print(f"✓ Backup created: {backup_file}")
        
        # 파일 내용 읽기
        with open(lightglue_file, 'r') as f:
            content = f.read()
        
        # 이미 패치되었는지 확인
        if 'LIGHTGLUE_OFFLINE_PATCH' in content:
            print("✓ LightGlue already patched")
            return True
        
        # 오프라인 패치 코드
        patch_code = '''# LIGHTGLUE_OFFLINE_PATCH
import torch
from pathlib import Path

def _offline_load_state_dict_from_url(url, *args, **kwargs):
    """Offline version that loads pre-downloaded models"""
    model_name = url.split('/')[-1]
    cache_dir = Path("/home/user/.cache/torch/hub/checkpoints")
    
    # 직접 파일명 매칭
    if cache_dir.exists():
        target_file = cache_dir / model_name
        if target_file.exists():
            print(f"Loading pre-downloaded model: {target_file}")
            return torch.load(target_file, map_location=kwargs.get('map_location', 'cpu'))
    
    raise FileNotFoundError(f"Pre-downloaded model not found: {model_name}")

# torch.hub.load_state_dict_from_url을 오프라인 버전으로 교체
original_torch_hub_load = torch.hub.load_state_dict_from_url
torch.hub.load_state_dict_from_url = _offline_load_state_dict_from_url

'''
        
        # import 섹션 끝에 패치 코드 삽입
        import_section_end = content.find('\nclass ')
        if import_section_end > 0:
            patched_content = content[:import_section_end] + '\n\n' + patch_code + '\n' + content[import_section_end:]
        else:
            patched_content = patch_code + '\n\n' + content
        
        # 파일 저장
        with open(lightglue_file, 'w') as f:
            f.write(patched_content)
        
        print("✓ LightGlue offline patch applied successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: LightGlue patch failed: {e}")
        return False


def patch_hloc_lightglue():
    """hloc의 LightGlue matcher도 패치"""
    try:
        import hloc.matchers.lightglue as hloc_lg
        hloc_lg_file = Path(hloc_lg.__file__)
        
        with open(hloc_lg_file, 'r') as f:
            hloc_content = f.read()
        
        if 'HLOC_LIGHTGLUE_OFFLINE_PATCH' in hloc_content:
            print("✓ hloc LightGlue matcher already patched")
            return True
        
        # hloc용 패치 코드
        hloc_patch = '''# HLOC_LIGHTGLUE_OFFLINE_PATCH
import torch
from pathlib import Path

def _offline_load_state_dict_from_url(url, *args, **kwargs):
    """Offline version for hloc LightGlue matcher"""
    model_name = url.split('/')[-1]
    cache_dir = Path("/home/user/.cache/torch/hub/checkpoints")
    
    if cache_dir.exists():
        target_file = cache_dir / model_name
        if target_file.exists():
            print(f"[HLOC] Loading pre-downloaded model: {target_file}")
            return torch.load(target_file, map_location=kwargs.get('map_location', 'cpu'))
    
    raise FileNotFoundError(f"[HLOC] Pre-downloaded model not found: {model_name}")

torch.hub.load_state_dict_from_url = _offline_load_state_dict_from_url

'''
        
        # 파일 앞부분에 패치 삽입
        hloc_patched = hloc_patch + '\n\n' + hloc_content
        
        with open(hloc_lg_file, 'w') as f:
            f.write(hloc_patched)
        
        print("✓ hloc LightGlue matcher patched for offline mode")
        return True
        
    except Exception as e:
        print(f"⚠ hloc LightGlue patch skipped: {e}")
        return False


if __name__ == "__main__":
    print("=== Applying LightGlue offline patches ===")
    
    success = True
    success &= patch_lightglue()
    success &= patch_hloc_lightglue()
    
    if success:
        print("✅ All LightGlue patches applied successfully")
        sys.exit(0)
    else:
        print("❌ Some LightGlue patches failed")
        sys.exit(1)