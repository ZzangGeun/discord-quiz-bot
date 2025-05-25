# Discord Quiz Bot 🤖

24/7 자동으로 실행되는 Discord 퀴즈 봇입니다. Gemini AI를 활용하여 코딩테스트, 알고리즘, SQL 관련 퀴즈를 자동으로 생성하고 Discord 채널에 전송합니다.

## 🚀 주요 기능

- **자동 퀴즈 생성**: 1시간마다 Gemini AI가 새로운 퀴즈를 생성
- **자동 전송**: 10분마다 새로운 퀴즈를 Discord 채널에 자동 전송
- **슬래시 명령어**: `/퀴즈`, `/답` 명령어로 수동 퀴즈 요청 및 답 확인
- **데이터베이스**: SQLite로 퀴즈 저장 및 관리
- **24/7 호스팅**: Replit에서 무료로 24시간 실행

## 📋 환경 변수 설정 (Replit Secrets)

Replit에서 다음 환경 변수들을 설정해주세요:

1. **BOT_TOKEN**: Discord 봇 토큰
   - Discord Developer Portal에서 발급받은 봇 토큰

2. **QUIZ_CHANNEL_ID**: 퀴즈를 전송할 Discord 채널 ID
   - Discord에서 채널 우클릭 → "링크 복사" → ID 추출

3. **GEMINI_API_KEY**: Google Gemini AI API 키
   - Google AI Studio에서 발급받은 API 키

## 🔧 Replit 배포 방법

### 1단계: 프로젝트 업로드
1. Replit에 로그인
2. "Create Repl" → "Import from GitHub" 또는 파일 직접 업로드
3. 모든 프로젝트 파일들을 업로드

### 2단계: 환경 변수 설정
1. Replit 사이드바에서 "Secrets" (🔒) 클릭
2. 다음 환경 변수들을 추가:
   ```
   Key: BOT_TOKEN
   Value: 여러분의_디스코드_봇_토큰

   Key: QUIZ_CHANNEL_ID  
   Value: 여러분의_채널_ID

   Key: GEMINI_API_KEY
   Value: 여러분의_제미나이_API_키
   ```

### 3단계: 실행
1. Replit에서 "Run" 버튼 클릭
2. `main_replit.py`가 자동으로 실행됩니다
3. 콘솔에서 시스템 시작 메시지 확인

### 4단계: 24/7 실행 설정
1. Replit "Always On" 기능 활성화 (무료 플랜에서도 가능)
2. Keep-alive 서버가 자동으로 봇을 계속 실행시킵니다

## 📁 파일 구조

```
discord_bot/
├── main_replit.py          # Replit 메인 실행 파일
├── discord_bot.py          # Discord 봇 로직
├── gemini_query_bot.py     # AI 퀴즈 생성 및 스케줄링
├── keep_alive.py           # Replit Keep-alive 서버
├── config.py               # 환경 변수 설정
├── ai_quiz_functions.py    # 문자열 처리 유틸리티
├── requirements.txt        # Python 패키지 의존성
├── .replit                 # Replit 설정 파일
├── replit.nix             # Nix 환경 설정
└── README.md              # 이 파일
```

## 🎮 봇 명령어

### 슬래시 명령어
- `/퀴즈`: 수동으로 퀴즈를 요청합니다
- `/답`: 최신 퀴즈의 정답을 확인합니다
- `/답 [퀴즈_ID]`: 특정 퀴즈의 정답을 확인합니다

## 📊 퀴즈 형식

```
오늘의 문제- 다음 중 SQL DML에서 데이터를 삭제하는 명령어는 무엇인가요?
a) SELECT
b) INSERT  
c) UPDATE
d) DELETE
;답: (d)
```

## ⚡ 자동화 시스템

- **퀴즈 생성**: 매 1시간마다 새로운 퀴즈 자동 생성
- **퀴즈 전송**: 매 10분마다 새로운 퀴즈가 있는지 확인하여 Discord에 전송
- **데이터베이스**: 모든 퀴즈는 SQLite에 저장되어 관리

## 🐛 문제 해결

### 봇이 응답하지 않는 경우
1. Replit Secrets에서 환경 변수가 올바르게 설정되었는지 확인
2. Discord 봇 토큰이 유효한지 확인
3. 봇이 해당 Discord 서버에 초대되었는지 확인

### API 오류가 발생하는 경우
1. Gemini API 키가 유효한지 확인
2. API 할당량이 남아있는지 확인

### Keep-alive 관련
- Flask 서버가 포트 8080에서 실행됩니다
- `/` 경로에서 봇 상태를 확인할 수 있습니다

## 💡 추가 기능 확장

- 퀴즈 카테고리 추가
- 사용자별 점수 시스템
- 퀴즈 난이도 조절
- 웹 대시보드 추가

## 📝 라이센스

이 프로젝트는 개인 학습 및 연구 목적으로 자유롭게 사용할 수 있습니다.
