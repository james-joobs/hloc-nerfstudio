#!/usr/bin/env python3
"""
Final verification script for Docker build
"""

import sys
import subprocess
import os

def main():
    print("=== Final Environment Verification ===")
    
    # Check CUDA toolkit installation
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'release' in line:
                    print(f"✅ nvcc version: {line.strip()}")
                    break
        else:
            print("❌ nvcc not found")
    except FileNotFoundError:
        print("❌ nvcc command not found")
    
    # Check CUDA directories
    cuda_dir = "/usr/local/cuda-12.8"
    if os.path.exists(cuda_dir):
        print(f"✅ CUDA 12.8 directory found: {cuda_dir}")
        nvcc_path = f"{cuda_dir}/bin/nvcc"
        if os.path.exists(nvcc_path):
            print(f"✅ nvcc compiler found: {nvcc_path}")
        else:
            print(f"❌ nvcc not found at: {nvcc_path}")
    else:
        print(f"❌ CUDA directory not found: {cuda_dir}")
    
    # Check CUDA architectures
    try:
        import torch
        arch_list = torch.cuda.get_arch_list()
        sm120_support = "sm_120" in str(arch_list)
        print(f"PyTorch CUDA architectures: {arch_list}")
        print(f"RTX 5090 sm_120 support: {sm120_support}")
    except Exception as e:
        print(f"CUDA architecture check failed: {e}")
    
    # Check gsplat
    try:
        import gsplat
        print(f"✅ gsplat version: {gsplat.__version__}")
        
        # Check if gsplat was compiled with CUDA
        if hasattr(gsplat, '__cuda_version__'):
            print(f"gsplat CUDA version: {gsplat.__cuda_version__}")
        
        print("✅ gsplat imported successfully")
    except ImportError as e:
        print(f"⚠ gsplat import error: {e}")
    except Exception as e:
        print(f"⚠ gsplat error: {e}")
    
    print("✅ Final verification completed")

if __name__ == "__main__":
    main()