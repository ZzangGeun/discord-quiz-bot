#!/bin/bash
# Replit 패키지 설치 스크립트

echo "🔧 Replit 환경에서 패키지 설치 중..."

# pip 업그레이드
python -m pip install --upgrade pip

# requirements.txt 패키지 설치
python -m pip install -r requirements.txt

echo "✅ 패키지 설치 완료!"
echo "🚀 이제 main_replit.py를 실행하세요."
