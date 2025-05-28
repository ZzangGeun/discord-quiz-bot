import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from ai_quiz_functions import process_string_by_argument
from config import BOT_TOKEN, QUIZ_CHANNEL_ID
from database_helper import get_db_connection, init_database, IS_RAILWAY

intents = discord.Intents.default()
intents.message_content = False
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} 봇이 준비되었습니다!')
    print(f"타겟 채널 ID: {QUIZ_CHANNEL_ID}")

    init_database()

    try:
        synced = await bot.tree.sync()
        print(f"슬래시 명령어 {len(synced)}개 동기화 완료")
    except Exception as e:
        print(f"슬래시 명령어 동기화 실패: {e}")

    send_quiz_task.start()
    send_answer_task.start()

@tasks.loop(minutes=1)
async def send_quiz_task():
    """매일 9, 12, 15, 18, 21시에만 퀴즈 전송"""
    try:
        now = datetime.now()
        if now.minute == 0 and now.hour in [9, 12, 15, 18, 21]:
            conn = get_db_connection()
            cursor = conn.cursor()

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

                if isinstance(channel, discord.TextChannel):
                    quiz_only = process_string_by_argument(quiz_content, '1')
                    await channel.send(f"🎯 **퀴즈 #{quiz_id}**\n{quiz_only}\n\n⏰ *30분 후에 정답이 공개됩니다!*")

                    cursor.execute('''
                        UPDATE quizzes 
                        SET sent_to_discord = TRUE, quiz_sent_at = ? 
                        WHERE id = ?
                    ''', (now, quiz_id))

                    conn.commit()
                    print(f"✅ 퀴즈 ID {quiz_id} 전송 완료")
                else:
                    print(f"❌ 채널 ID {QUIZ_CHANNEL_ID}는 텍스트 채널이 아닙니다.")
            conn.close()
    except Exception as e:
        print(f"❌ 퀴즈 전송 중 오류: {e}")

@tasks.loop(minutes=1)
async def send_answer_task():
    """퀴즈 전송 후 30분이 지난 퀴즈의 정답 전송"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        threshold = datetime.now() - timedelta(minutes=30)

        cursor.execute('''
            SELECT id, content FROM quizzes 
            WHERE sent_to_discord = TRUE 
            AND answer_sent = FALSE 
            AND quiz_sent_at IS NOT NULL 
            AND quiz_sent_at <= ?
            ORDER BY quiz_sent_at ASC
        ''', (threshold,))
        
        results = cursor.fetchall()
        
        for quiz_id, quiz_content in results:
            channel = bot.get_channel(QUIZ_CHANNEL_ID)
            if isinstance(channel, discord.TextChannel):
                answer = process_string_by_argument(quiz_content, '2')
                await channel.send(f"💡 **퀴즈 #{quiz_id} 정답 공개!**\n{answer}")
                cursor.execute('''
                    UPDATE quizzes 
                    SET answer_sent = TRUE, answer_sent_at = ? 
                    WHERE id = ?
                ''', (datetime.now(), quiz_id))
                conn.commit()
                print(f"✅ 퀴즈 ID {quiz_id} 정답 전송 완료")
        conn.close()
    except Exception as e:
        print(f"❌ 정답 전송 중 오류: {e}")

@bot.tree.command(name="답", description="퀴즈의 답을 보여줍니다")
@app_commands.describe(quiz_id="특정 퀴즈 ID (생략시 최신 퀴즈)")
async def show_answer(interaction: discord.Interaction, quiz_id: Optional[int] = None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if quiz_id:
            cursor.execute('SELECT content FROM quizzes WHERE id = ?', (quiz_id,))
        else:
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
            cursor.execute('''
                SELECT content FROM quizzes 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            fallback = cursor.fetchone()
            if fallback:
                quiz_content = fallback[0]
                answer = process_string_by_argument(quiz_content, '2')
                await interaction.response.send_message(f"💡 **정답 (최신 퀴즈):** {answer}")
            else:
                await interaction.response.send_message("❌ 저장된 퀴즈가 없습니다.")
        conn.close()
    except Exception as e:
        await interaction.response.send_message(f"❌ 오류 발생: {e}")
        print(f"❌ show_answer 오류: {e}")

@bot.tree.command(name="퀴즈", description="수동으로 퀴즈를 요청합니다")
async def manual_quiz(interaction: discord.Interaction):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

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
        else:
            await interaction.response.send_message("❌ 저장된 퀴즈가 없습니다.")
        conn.close()
    except Exception as e:
        await interaction.response.send_message(f"❌ 오류 발생: {e}")
        print(f"❌ manual_quiz 오류: {e}")

if __name__ == "__main__":
    if BOT_TOKEN:
        bot.run(BOT_TOKEN)
    else:
        print("❌ BOT_TOKEN이 설정되지 않았습니다. 환경변수를 확인해주세요.")
