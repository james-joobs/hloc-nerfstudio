#!/bin/bash

# LightGlue 및 관련 모델들을 미리 다운로드하는 스크립트

MODELS_DIR="./models_cache"
mkdir -p "$MODELS_DIR"

echo "=== Downloading LightGlue and related models ==="

# PyTorch hub 모델들 (LightGlue, AlexNet 등)
declare -A MODELS=(
    ["superpoint_lightglue.pth"]="https://github.com/cvg/LightGlue/releases/download/v0.1_arxiv/superpoint_lightglue.pth"
    ["disk_lightglue.pth"]="https://github.com/cvg/LightGlue/releases/download/v0.1_arxiv/disk_lightglue.pth"
    ["aliked_lightglue.pth"]="https://github.com/cvg/LightGlue/releases/download/v0.1_arxiv/aliked_lightglue.pth"
    ["sift_lightglue.pth"]="https://github.com/cvg/LightGlue/releases/download/v0.1_arxiv/sift_lightglue.pth"
    ["superpoint_v1.pth"]="https://github.com/magicleap/SuperGluePretrainedNetwork/raw/master/models/weights/superpoint_v1.pth"
    ["alexnet-owt-7be5be79.pth"]="https://download.pytorch.org/models/alexnet-owt-7be5be79.pth"
)

# NetVLAD 모델들
declare -A NETVLAD_MODELS=(
    ["VGG16-NetVLAD-Pitts30K.mat"]="https://cvg-data.inf.ethz.ch/hloc/netvlad/Pitts30K_struct.mat"
    ["VGG16-NetVLAD-TokyoTM.mat"]="https://cvg-data.inf.ethz.ch/hloc/netvlad/TokyoTM_struct.mat"
)

# LightGlue 모델 다운로드
for MODEL_NAME in "${!MODELS[@]}"; do
    URL="${MODELS[$MODEL_NAME]}"
    OUTPUT_FILE="$MODELS_DIR/$MODEL_NAME"
    
    if [ -f "$OUTPUT_FILE" ]; then
        echo "✓ $MODEL_NAME already exists"
    else
        echo "Downloading $MODEL_NAME..."
        wget -q --show-progress -O "$OUTPUT_FILE" "$URL"
        if [ $? -eq 0 ]; then
            echo "✓ Downloaded $MODEL_NAME"
        else
            echo "✗ Failed to download $MODEL_NAME"
        fi
    fi
done

# NetVLAD 모델 다운로드
for MODEL_NAME in "${!NETVLAD_MODELS[@]}"; do
    URL="${NETVLAD_MODELS[$MODEL_NAME]}"
    OUTPUT_FILE="$MODELS_DIR/$MODEL_NAME"
    
    if [ -f "$OUTPUT_FILE" ]; then
        echo "✓ $MODEL_NAME already exists"
    else
        echo "Downloading $MODEL_NAME..."
        wget -q --show-progress -O "$OUTPUT_FILE" "$URL"
        if [ $? -eq 0 ]; then
            echo "✓ Downloaded $MODEL_NAME"
        else
            echo "✗ Failed to download $MODEL_NAME"
        fi
    fi
done

echo ""
echo "=== Download Summary ==="
echo "Models directory: $MODELS_DIR"
echo "Downloaded files:"
ls -lh "$MODELS_DIR" | grep -E "\.(pth|mat)$"
echo ""
echo "✅ All models downloaded successfully!"
echo ""
echo "Now you can build the Docker image with:"
echo "docker-compose build nerfstudio"