# 🤖 Discord Quiz Bot

AI 기반 자동 퀴즈 생성 및 전송 시스템입니다. Gemini AI를 활용하여 코딩테스트, 알고리즘, SQL 등의 문제를 자동으로 생성하고 Discord 채널에 전송합니다.

## ✨ 주요 기능

- 🎯 **AI 퀴즈 자동 생성**: Gemini AI로 다양한 프로그래밍 문제 생성
- ⏰ **자동 일정 관리**: 3시간마다 새 퀴즈 전송, 30분 후 정답 공개
- 💬 **Discord 통합**: 슬래시 명령어 지원 (`/퀴즈`, `/답`)
- 🗄️ **스마트 데이터베이스**: 환경별 자동 감지 (로컬: SQLite 파일, Railway: 메모리)
- 🚂 **Railway 배포**: 24/7 무료 호스팅 지원
- ⭐ **구분자 시스템**: `★` 구분자로 문제와 답안 분리

## 🏗️ 시스템 아키텍처

```
📁 Discord Quiz Bot
├── 🤖 AI 퀴즈 생성기 (gemini_query_bot.py)
│   ├── Gemini API 연동
│   ├── 1시간마다 자동 퀴즈 생성
│   └── 데이터베이스 저장
│
├── 🎮 Discord 봇 (discord_bot.py)
│   ├── 3시간마다 퀴즈 전송
│   ├── 30분 후 정답 공개
│   └── 슬래시 명령어 처리
│
├── 🗄️ 데이터베이스 헬퍼 (database_helper.py)
│   ├── 환경별 자동 감지
│   ├── 로컬: SQLite 파일
│   └── Railway: 메모리 DB
│
└── 🚀 배포 시스템 (main_railway.py)
    ├── 멀티스레드 관리
    └── Railway 최적화
```

## 🛠️ 설치 및 설정

### 1. 환경 요구사항

- Python 3.8+
- Discord Bot Token
- Google Gemini API Key
- Discord 채널 ID

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

#### 로컬 개발용 (.env 파일)
```env
BOT_TOKEN=your_discord_bot_token_here
QUIZ_CHANNEL_ID=your_discord_channel_id_here
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Railway 배포용 (Railway Variables)
- `BOT_TOKEN`: Discord 봇 토큰
- `QUIZ_CHANNEL_ID`: Discord 채널 ID
- `GEMINI_API_KEY`: Google Gemini API 키

## 🚀 실행 방법

### 로컬 실행
```bash
# 데이터베이스 테스트
python test_database.py

# Gemini API 테스트
python test_gemini_local.py

# Discord 봇 실행
python discord_bot.py

# 퀴즈 생성기 실행
python gemini_query_bot.py
```

### Railway 배포
```bash
# Railway CLI로 배포
railway up

# 또는 GitHub 연결 후 자동 배포
```

## 📋 사용법

### Discord 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/퀴즈` | 최신 퀴즈 수동 요청 | `/퀴즈` |
| `/답` | 정답 보기 (ID 선택 가능) | `/답` 또는 `/답 quiz_id:3` |

### 자동 스케줄

- **📝 퀴즈 생성**: 30분마다
- **📨 퀴즈 전송**: 3시간마다
- **💡 정답 공개**: 퀴즈 전송 2시간 후

## 🎯 퀴즈 형식

### 객관식 예시
```
🎯 퀴즈 #1
오늘의 문제- 다음 중 SQL DML에서 데이터를 삭제하는 명령어는?
a) SELECT
b) INSERT
c) UPDATE
d) DELETE

⏰ 2시간 후에 정답이 공개됩니다!
```

### 주관식 예시
```
🎯 퀴즈 #2
오늘의 문제- 파이썬에서 리스트의 모든 요소를 제곱하는 함수를 작성하세요.

⏰ 2시간 후에 정답이 공개됩니다!
```

### 정답 공개
```
💡 퀴즈 #1 정답 공개!
답: (d) DELETE
```

## 📁 파일 구조

```
discord_bot_clean/
├── 📄 README.md                 # 프로젝트 문서
├── 🤖 main_railway.py          # Railway 배포용 메인
├── 🎮 discord_bot.py           # Discord 봇 핵심
├── 🧠 gemini_query_bot.py      # AI 퀴즈 생성기
├── 🗄️ database_helper.py       # 데이터베이스 헬퍼
├── ⚙️ config.py                # 설정 관리
├── 🔧 ai_quiz_functions.py     # 퀴즈 처리 함수
├── 📝 cote_bot.txt             # 퀴즈 백업 파일
├── 🚂 railway.json             # Railway 설정
├── 📦 requirements.txt         # Python 의존성
├── 🐳 Procfile                 # Railway 실행 명령
└── 🗃️ quiz_database.db         # SQLite 데이터베이스 (로컬)
```

## 🔧 주요 설정

### Gemini AI 설정
- **모델**: `gemini-2.5-flash-preview-04-17`
- **Temperature**: 1.5 (다양성 보장)
- **최대 토큰**: 1500

### Discord 봇 권한
- `Send Messages`
- `Use Slash Commands`
- `Read Message History`

### 데이터베이스 스키마
```sql
CREATE TABLE quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_to_discord BOOLEAN DEFAULT FALSE,
    quiz_sent_at TIMESTAMP NULL,
    answer_sent BOOLEAN DEFAULT FALSE,
    answer_sent_at TIMESTAMP NULL
);
```

## 🐛 문제 해결

### 일반적인 문제

1. **환경변수 미설정**
   ```
   ❌ BOT_TOKEN 환경변수를 설정해주세요!
   ```
   → `.env` 파일 또는 Railway Variables 확인

2. **Gemini API 오류**
   ```
   ❌ Gemini API에서 빈 응답을 받았습니다.
   ```
   → API 키 확인 및 할당량 체크

3. **데이터베이스 연결 실패**
   ```
   ❌ 데이터베이스 테스트 실패
   ```
   → `test_database.py` 실행하여 진단

4. **Discord Intent 경고 (정상 작동)**
   ```
   [WARNING] Privileged message content intent is missing
   ```
   → 슬래시 명령어만 사용하므로 문제없음. 경고 무시 가능

### 로그 확인 방법

```bash
# Railway 로그 확인
railway logs

# 로컬 디버그 모드
python main_railway.py
```

## 📊 모니터링

### 성공적인 동작 로그
```
✅ 퀴즈 ID 3 생성 완료!
✅ 퀴즈 ID 2 전송 완료 - 2시간 후답변 예정
✅ 퀴즈 ID 2 답변 전송 완료
```

### 환경 상태 확인
```
🗄️ 데이터베이스 모드: 메모리 (Railway)
🚂 Railway 환경: 메모리 기반 SQLite 사용
```

## 💰 Railway 배포 비용

- **무료 크레딧**: 월 $5
- **24/7 운영**: 가능
- **자동 스케일링**: 지원
- **도메인**: 무료 제공

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 📞 지원

문제가 발생하거나 도움이 필요한 경우:

1. **Issues**: GitHub Issues에 문제 보고
2. **테스트**: 로컬 테스트 스크립트 실행
3. **로그**: Railway/로컬 로그 확인

---

## 🎉 현재 상태

✅ **완료된 기능**
- AI 퀴즈 자동 생성 (Gemini)
- Discord 자동 전송 (3시간 간격)
- 정답 자동 공개 (2시간 후)
- 슬래시 명령어 지원
- Railway 24/7 호스팅
- 구분자 시스템 (★)
- 환경별 데이터베이스 자동 감지

🔄 **개선 예정**
- 퀴즈 다양성 증대
- 사용자 피드백 시스템
- 통계 및 분석 기능

---

*Made with ❤️ for better coding practice*
