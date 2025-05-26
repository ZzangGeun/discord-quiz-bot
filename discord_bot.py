import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from ai_quiz_functions import process_string_by_argument
from config import BOT_TOKEN, QUIZ_CHANNEL_ID
from database_helper import get_db_connection, init_database, IS_RAILWAY

# 봇 설정 (슬래시 명령어만 사용하므로 메시지 내용 권한 불필요)
intents = discord.Intents.default()
intents.message_content = False  # 메시지 내용 읽기 비활성화로 경고 제거
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} 봇이 준비되었습니다!')
    print(f"타겟 채널 ID: {QUIZ_CHANNEL_ID}")
    
    # 데이터베이스 초기화
    init_database()
    
    # 슬래시 명령어 동기화
    try:
        synced = await bot.tree.sync()
        print(f"슬래시 명령어 {len(synced)}개 동기화 완료")
    except Exception as e:
        print(f"슬래시 명령어 동기화 실패: {e}")
    
    send_quiz_task.start()  # 퀴즈 전송 태스크 시작
    send_answer_task.start()  # 답변 전송 태스크 시작

@tasks.loop(hours=3)  # 3시간마다 새로운 퀴즈 확인
async def send_quiz_task():
    """DB에서 새로운 퀴즈를 확인하고 디스코드에 전송"""
    try:
        if QUIZ_CHANNEL_ID is None:
            print("⚠️ QUIZ_CHANNEL_ID가 설정되지 않았습니다. 환경변수를 확인해주세요.")
            return
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 아직 전송되지 않은 퀴즈 가져오기
        cursor.execute('''
            SELECT id, content FROM quizzes 
            WHERE sent_to_discord = FALSE 
            ORDER BY created_at ASC 
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        
        if result:
            quiz_id, quiz_content = result
            channel = bot.get_channel(QUIZ_CHANNEL_ID)
            
            # 텍스트 채널인지 확인
            if isinstance(channel, discord.TextChannel):
                # 퀴즈 문제만 추출 (답 제외)
                quiz_only = process_string_by_argument(quiz_content, '1')
                await channel.send(f"🎯 **퀴즈 #{quiz_id}**\n{quiz_only}\n\n⏰ *1시간 후에 정답이 공개됩니다!*")
                
                # 전송 완료 표시 및 전송 시간 기록
                cursor.execute('''
                    UPDATE quizzes 
                    SET sent_to_discord = TRUE, quiz_sent_at = ? 
                    WHERE id = ?
                ''', (datetime.now(), quiz_id))
                
                conn.commit()
                print(f"✅ 퀴즈 ID {quiz_id} 전송 완료 - 1시간 후 답변 예정")
            else:
                print(f"❌ 채널 ID {QUIZ_CHANNEL_ID}는 텍스트 채널이 아닙니다.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 퀴즈 전송 중 오류: {e}")

@tasks.loop(minutes=30)  # 30분마다 답변 전송 확인
async def send_answer_task():
    """30분이 지난 퀴즈의 답변을 전송"""
    try:
        if QUIZ_CHANNEL_ID is None:
            print("⚠️ QUIZ_CHANNEL_ID가 설정되지 않았습니다. 환경변수를 확인해주세요.")
            return
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 30분이 지났고 아직 답변이 전송되지 않은 퀴즈 찾기
        thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
        
        cursor.execute('''
            SELECT id, content FROM quizzes 
            WHERE sent_to_discord = TRUE 
            AND answer_sent = FALSE 
            AND quiz_sent_at IS NOT NULL 
            AND quiz_sent_at <= ?
            ORDER BY quiz_sent_at ASC
        ''', (thirty_minutes_ago,))
        
        results = cursor.fetchall()
        
        for quiz_id, quiz_content in results:
            channel = bot.get_channel(QUIZ_CHANNEL_ID)
            
            # 텍스트 채널인지 확인
            if isinstance(channel, discord.TextChannel):
                # 답변만 추출
                answer = process_string_by_argument(quiz_content, '2')
                await channel.send(f"💡 **퀴즈 #{quiz_id} 정답 공개!**\n{answer}")
                
                # 답변 전송 완료 표시
                cursor.execute('''
                    UPDATE quizzes 
                    SET answer_sent = TRUE, answer_sent_at = ? 
                    WHERE id = ?
                ''', (datetime.now(), quiz_id))
                
                conn.commit()
                print(f"✅ 퀴즈 ID {quiz_id} 답변 전송 완료")
            else:
                print(f"❌ 채널 ID {QUIZ_CHANNEL_ID}는 텍스트 채널이 아닙니다.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 답변 전송 중 오류: {e}")

@bot.tree.command(name="답", description="퀴즈의 답을 보여줍니다")
@app_commands.describe(quiz_id="특정 퀴즈 ID (생략시 최신 퀴즈)")
async def show_answer(interaction: discord.Interaction, quiz_id: Optional[int] = None):
    """퀴즈의 답을 보여주는 슬래시 명령어"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 디버그: 전체 퀴즈 수 확인
        cursor.execute('SELECT COUNT(*) FROM quizzes')
        total_count = cursor.fetchone()[0]
        print(f"🔍 디버그 - 전체 퀴즈 수: {total_count}")
        
        # 디버그: 전송된 퀴즈 수 확인
        cursor.execute('SELECT COUNT(*) FROM quizzes WHERE sent_to_discord = TRUE')
        sent_count = cursor.fetchone()[0]
        print(f"🔍 디버그 - 전송된 퀴즈 수: {sent_count}")
        
        if quiz_id:
            cursor.execute('SELECT content FROM quizzes WHERE id = ?', (quiz_id,))
            print(f"🔍 디버그 - 특정 ID {quiz_id} 검색 중")
        else:
            # 가장 최근 퀴즈 (전송 여부 상관없이) 먼저 시도
            cursor.execute('''
                SELECT id, content, sent_to_discord FROM quizzes 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            debug_result = cursor.fetchone()
            if debug_result:
                debug_id, debug_content, debug_sent = debug_result
                print(f"🔍 디버그 - 최신 퀴즈 ID: {debug_id}, 전송됨: {debug_sent}")
            
            # 원래 쿼리 실행
            cursor.execute('''
                SELECT content FROM quizzes 
                WHERE sent_to_discord = TRUE 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
        
        result = cursor.fetchone()
        
        if result:
            quiz_content = result[0]
            answer = process_string_by_argument(quiz_content, '2')
            await interaction.response.send_message(f"💡 **정답:** {answer}")
        else:
            # 대안: 전송 여부와 상관없이 최신 퀴즈의 답 제공
            cursor.execute('''
                SELECT content FROM quizzes 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            fallback_result = cursor.fetchone()
            
            if fallback_result:
                quiz_content = fallback_result[0]
                answer = process_string_by_argument(quiz_content, '2')
                await interaction.response.send_message(f"💡 **정답 (최신 퀴즈):** {answer}")
            else:
                await interaction.response.send_message(f"❌ 저장된 퀴즈가 없습니다. (전체: {total_count}개, 전송: {sent_count}개)")
        
        conn.close()
        
    except Exception as e:
        await interaction.response.send_message(f"❌ 오류가 발생했습니다: {e}")
        print(f"❌ show_answer 오류: {e}")
        import traceback
        traceback.print_exc()

@bot.tree.command(name="퀴즈", description="수동으로 퀴즈를 요청합니다")
async def manual_quiz(interaction: discord.Interaction):
    """수동으로 퀴즈를 요청하는 슬래시 명령어"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 디버그: 전체 퀴즈 수 확인
        cursor.execute('SELECT COUNT(*) FROM quizzes')
        total_count = cursor.fetchone()[0]
        print(f"🔍 퀴즈 요청 - 전체 퀴즈 수: {total_count}")
        
        cursor.execute('''
            SELECT id, content FROM quizzes 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        
        if result:
            quiz_id, quiz_content = result
            quiz_only = process_string_by_argument(quiz_content, '1')
            await interaction.response.send_message(f"🎯 **수동 퀴즈 #{quiz_id}**\n{quiz_only}")
            print(f"✅ 수동 퀴즈 ID {quiz_id} 전송 성공")
        else:
            await interaction.response.send_message(f"❌ 저장된 퀴즈가 없습니다. (전체 개수: {total_count})")
        
        conn.close()
        
    except Exception as e:
        await interaction.response.send_message(f"❌ 오류가 발생했습니다: {e}")
        print(f"❌ manual_quiz 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if BOT_TOKEN:
        bot.run(BOT_TOKEN)
    else:
        print("❌ BOT_TOKEN이 설정되지 않았습니다. 환경변수를 확인해주세요.")
