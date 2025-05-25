# Discord 봇 설정 파일 - Replit 버전
# 환경변수 (Replit Secrets) 우선, 없으면 .env 파일, 최후에 기본값

import os

# .env 파일 로드 시도 (로컬 개발용, Replit에서는 Secrets 사용)
try:
    from dotenv import load_dotenv
    # .env 파일 로드 (절대 경로로 지정)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '.env')
    load_dotenv(env_path)
    print("✅ .env 파일을 로드했습니다 (로컬 개발 모드)")
except ImportError:
    print("📝 python-dotenv가 없습니다. Replit Secrets 또는 환경변수를 사용합니다.")
except Exception as e:
    print(f"⚠️ .env 파일 로드 중 오류: {e}")

# 환경변수에서 설정 가져오기 (Replit Secrets 지원)
BOT_TOKEN = os.getenv('BOT_TOKEN')
QUIZ_CHANNEL_ID = int(os.getenv('QUIZ_CHANNEL_ID', '0')) if os.getenv('QUIZ_CHANNEL_ID') else None
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 기타 설정
QUIZ_INTERVAL_HOURS = int(os.getenv('QUIZ_INTERVAL_HOURS', '1'))
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '10'))

# 웹훅 URL (백업용)
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
