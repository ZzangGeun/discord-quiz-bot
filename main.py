"""
Discord Quiz Bot - Replit 버전
1시간마다 자동으로 퀴즈를 생성하고 Discord 봇이 자동으로 전송하는 시스템
"""

import os
import threading
import time
from keep_alive import keep_alive

# 환경변수에서 설정 가져오기
BOT_TOKEN = os.getenv('BOT_TOKEN')
QUIZ_CHANNEL_ID = os.getenv('QUIZ_CHANNEL_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def check_config():
    """설정 확인"""
    if not BOT_TOKEN:
        print("❌ 오류: BOT_TOKEN 환경변수를 설정해주세요!")
        return False
    
    if not QUIZ_CHANNEL_ID:
        print("❌ 오류: QUIZ_CHANNEL_ID 환경변수를 설정해주세요!")
        return False
        
    if not GEMINI_API_KEY:
        print("❌ 오류: GEMINI_API_KEY 환경변수를 설정해주세요!")
        return False
    
    print("✅ 설정 확인 완료")
    print(f"📱 봇 토큰: {BOT_TOKEN[:20]}...")
    print(f"📢 채널 ID: {QUIZ_CHANNEL_ID}")
    return True

def run_quiz_generator():
    """퀴즈 생성기 실행"""
    from gemini_query_bot import run_scheduler
    print("🤖 퀴즈 생성기를 시작합니다...")
    try:
        run_scheduler()
    except Exception as e:
        print(f"❌ 퀴즈 생성기 오류: {e}")

def run_discord_bot():
    """Discord 봇 실행"""
    from discord_bot import bot
    from config import BOT_TOKEN
    print("🎮 Discord 봇을 시작합니다...")
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Discord 봇 오류: {e}")

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🎯 Discord Quiz Bot 시스템 시작")
    print("=" * 50)
    
    # 설정 확인
    if not check_config():
        print("\n❌ 설정을 완료한 후 다시 실행해주세요.")
        return
    print("\n🚀 시스템을 시작합니다...")
    print("📝 1시간마다 새로운 퀴즈가 생성됩니다.")
    print("📨 10분마다 새로운 퀴즈를 Discord에 자동 전송합니다.")
    print("⭐ 봇 명령어: /퀴즈, /답 (슬래시 명령어)")
    print("🛑 프로그램을 중단하려면 Ctrl+C를 누르세요.\n")
    
    try:
        # 퀴즈 생성기를 별도 스레드에서 실행
        quiz_thread = threading.Thread(target=run_quiz_generator)
        quiz_thread.daemon = True
        quiz_thread.start()
        
        # 잠시 대기 후 Discord 봇 실행
        time.sleep(3)
        
        # Discord 봇은 메인 스레드에서 실행
        run_discord_bot()
        
    except KeyboardInterrupt:
        print("\n🛑 시스템이 중단되었습니다.")
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")

if __name__ == "__main__":
    main()
