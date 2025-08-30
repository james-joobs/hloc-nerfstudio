#!/bin/bash

# hloc-nerfstudio 설정 및 실행 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== HLOC-NeRFStudio Setup Script ==="

# 필요한 디렉토리 생성
echo "Creating necessary directories..."
mkdir -p data outputs models

# 모델 다운로드 (선택사항)
if [ "$1" = "--download-models" ]; then
    echo "Downloading pre-trained models..."
    ./download_models.sh
fi

# Docker 이미지 빌드
echo "Building Docker image..."
docker-compose build hloc-nerfstudio

echo ""
echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  Start container:      docker-compose up -d hloc-nerfstudio"
echo "  Enter container:      docker-compose exec hloc-nerfstudio bash"
echo "  View logs:           docker-compose logs -f hloc-nerfstudio"
echo "  Stop container:      docker-compose down"
echo ""
echo "NeRFStudio viewer will be available at: http://localhost:7007"
echo ""
echo "Quick test commands inside container:"
echo "  ns-train nerfacto --help"
echo "  ns-viewer --help"
echo "  python -c \"import hloc; print('HLOC import successful')\""