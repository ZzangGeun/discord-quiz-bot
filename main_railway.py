"""
Discord Quiz Bot - Railway 버전
1시간마다 자동으로 퀴즈를 생성하고 Discord 봇이 자동으로 전송하는 시스템
Railway는 월 $5 무료 크레딧으로 24/7 실행 가능
"""

import os
import threading
import time
from config import BOT_TOKEN, QUIZ_CHANNEL_ID, GEMINI_API_KEY

def check_config():
    """설정 확인"""
    print("=" * 50)
    print("🚂 Discord Quiz Bot - Railway 배포")
    print("=" * 50)
    
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
    print(f"🤖 Gemini API: {GEMINI_API_KEY[:20]}...")
    return True

def run_quiz_generator():
    """퀴즈 생성기 실행"""
    try:
        from gemini_query_bot import run_scheduler
        print("🤖 퀴즈 생성기를 시작합니다...")
        run_scheduler()
    except Exception as e:
        print(f"❌ 퀴즈 생성기 오류: {e}")

def run_discord_bot():
    """Discord 봇 실행"""
    print("🎮 Discord 봇을 시작합니다...")
    try:
        # discord_bot.py에서 봇 가져와서 실행 (★ 구분자 및 30분 간격 기능 포함)
        from discord_bot import bot
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Discord 봇 오류: {e}")

def main():
    """메인 실행 함수"""
    # 설정 확인
    if not check_config():
        print("\n❌ 환경변수를 설정한 후 다시 실행해주세요.")
        print("Railway Variables에서 다음 변수들을 설정하세요:")
        print("- BOT_TOKEN")
        print("- QUIZ_CHANNEL_ID") 
        print("- GEMINI_API_KEY")
        return
        
    print("\n🚀 Railway에서 시스템을 시작합니다...")
    print("📝 1시간마다 새로운 퀴즈가 생성됩니다.")
    print("📨 3시간마다 새로운 퀴즈를 Discord에 자동 전송합니다.")
    print("💡 30분 후 자동으로 정답이 공개됩니다.")
    print("⭐ 봇 명령어: /퀴즈, /답 (슬래시 명령어)")
    print("🛤️ Railway 24/7 호스팅으로 안정적 운영\n")
    
    try:
        # 퀴즈 생성기를 별도 스레드에서 실행
        quiz_thread = threading.Thread(target=run_quiz_generator)
        quiz_thread.daemon = True
        quiz_thread.start()
        
        # 잠시 대기 후 Discord 봇 실행 (메인 스레드)
        time.sleep(3)
        run_discord_bot()
        
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")

if __name__ == "__main__":
    main()
