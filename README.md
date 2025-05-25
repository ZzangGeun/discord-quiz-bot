# 🤖 Discord AI Quiz Bot

Discord에서 자동으로 퀴즈를 생성하고 전송하는 AI 봇입니다.

## ✨ 주요 기능

- 🎯 **1시간마다 자동 퀴즈 생성** (Gemini AI 사용)
- 📨 **10분마다 자동 Discord 전송**
- ⏰ **30분 후 자동 정답 공개**
- 🎮 **슬래시 명령어 지원** (`/퀴즈`, `/답`)
- 🗄️ **SQLite 데이터베이스** 퀴즈 저장
- ☁️ **클라우드 배포 지원** (Railway, Replit 등)

## 🛠️ 설치 & 설정

### 1. 환경변수 설정
`.env.example`을 `.env`로 복사하고 다음 값들을 설정:

```bash
BOT_TOKEN=your_discord_bot_token
QUIZ_CHANNEL_ID=your_discord_channel_id  
GEMINI_API_KEY=your_gemini_api_key
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 봇 실행
```bash
python discord_bot_fixed.py
```

## 🚀 배포

### Railway 배포
1. GitHub에 코드 업로드
2. Railway에서 GitHub 저장소 연결
3. 환경변수 설정
4. 자동 배포 완료

### Replit 배포  
1. Replit에 코드 업로드
2. Secrets에 환경변수 설정
3. `main_replit.py` 실행

## 📋 명령어

- `/퀴즈` - 수동으로 최신 퀴즈 요청
- `/답 [퀴즈ID]` - 퀴즈 정답 확인

## 🔧 시스템 구조

- **퀴즈 생성**: `gemini_query_bot.py`
- **Discord 봇**: `discord_bot_fixed.py`
- **자동화**: 스케줄링 + 백그라운드 태스크
- **데이터베이스**: SQLite (`quiz_database.db`)

## 📄 라이선스

MIT License
