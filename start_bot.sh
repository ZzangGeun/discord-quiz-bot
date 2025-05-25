#!/bin/bash

echo "🚀 Discord Quiz Bot 시작 중..."
echo "📦 의존성 설치 중..."

# pip 업그레이드
pip install --upgrade pip

# 필요한 패키지 설치
pip install -r requirements.txt

echo "✅ 의존성 설치 완료"
echo "🤖 봇 시작..."

# 메인 봇 실행
python main_replit.py
