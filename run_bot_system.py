import subprocess
import threading
import time
import sys

def run_quiz_generator():
    """퀴즈 생성기 실행"""
    print("퀴즈 생성기를 시작합니다...")
    subprocess.run([sys.executable, "gemini_query_bot.py"])

def run_discord_bot():
    """디스코드 봇 실행"""
    print("디스코드 봇을 시작합니다...")
    subprocess.run([sys.executable, "discord_bot.py"])

if __name__ == "__main__":
    # 퀴즈 생성기를 별도 스레드에서 실행
    quiz_thread = threading.Thread(target=run_quiz_generator)
    quiz_thread.daemon = True
    quiz_thread.start()
    
    # 잠시 대기 후 디스코드 봇 실행
    time.sleep(2)
    
    # 디스코드 봇은 메인 스레드에서 실행
    run_discord_bot()
