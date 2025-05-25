import discord
from discord.ext import commands
import requests
import sqlite3
from ai_quiz_functions import *
from config import BOT_TOKEN, QUIZ_CHANNEL_ID
import sys

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} 봇이 준비되었습니다!')

async def send_quiz_to_discord(argument_value):
    """퀴즈를 Discord로 전송하는 함수"""
    try:
        # 파일에서 텍스트 읽어오기
        file_path = "./cote_bot.txt"
        
        with open(file_path, 'r', encoding='utf-8') as file:
            message_content = file.read()
        
        print(f"처리할 전체 문자열: \"{message_content}\"")
        
        # 문자열 처리 및 결과 출력
        result = process_string_by_argument(message_content, argument_value)
        print(f"매개변수 '{argument_value}'에 대한 결과:")
        print(result)
          # 채널 가져오기
        channel = bot.get_channel(QUIZ_CHANNEL_ID)
        if channel:
            await channel.send(result)
            print("메시지가 성공적으로 전송되었습니다.")
            
            # DB에도 저장 (선택사항)
            save_to_db(message_content, argument_value, result)
        else:
            print("채널을 찾을 수 없습니다. 채널 ID를 확인하세요.")
            
    except FileNotFoundError:
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

def save_to_db(original_content, argument_type, processed_content):
    """전송 내역을 DB에 저장"""
    try:
        conn = sqlite3.connect('quiz_database.db')
        cursor = conn.cursor()
        
        # 전송 내역 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_content TEXT,
                argument_type TEXT,
                processed_content TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT INTO sent_messages (original_content, argument_type, processed_content) 
            VALUES (?, ?, ?)
        ''', (original_content, argument_type, processed_content))
        
        conn.commit()
        conn.close()
        print("전송 내역이 DB에 저장되었습니다.")
    except Exception as e:
        print(f"DB 저장 중 오류: {e}")

@bot.command(name='전송')
async def send_quiz_command(ctx, arg_type: str = "1"):
    """수동으로 퀴즈를 전송하는 명령어"""
    if arg_type not in ["1", "2"]:
        await ctx.send("매개변수는 1 또는 2여야 합니다.")
        return
    
    await send_quiz_to_discord(arg_type)
    await ctx.send(f"매개변수 {arg_type}로 퀴즈를 전송했습니다.")

async def main():
    """메인 실행 함수"""
    if len(sys.argv) != 2:
        print("사용법: python quiz_discord.py [1 또는 2]")
        print("또는 봇을 실행한 후 '!전송 1' 또는 '!전송 2' 명령어를 사용하세요.")
        
        # 봇만 실행 (명령어 대기)
        await bot.start(BOT_TOKEN)
    else:
        argument_value = sys.argv[1]
        
        # 봇 시작 후 메시지 전송
        async def send_and_close():
            await bot.wait_until_ready()
            await send_quiz_to_discord(argument_value)
            await bot.close()
        
        # 백그라운드 태스크로 실행
        bot.loop.create_task(send_and_close())
        await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())