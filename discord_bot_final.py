import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
import pytz
from typing import Optional
from config import BOT_TOKEN, QUIZ_CHANNEL_ID
from database_helper import get_db_connection, init_database

# 한국 시간대 (KST) 반환 함수
def get_kst_now():
    kst = pytz.timezone('Asia/Seoul')
    return datetime.now(kst)

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
    check_and_send_answers.start()

@tasks.loop(minutes=1)
async def send_quiz_task():
    now = get_kst_now()
    
    # 오전 0시부터 9시까지는 퀴즈를 보내지 않음
    if 0 <= now.hour < 9:
        return
    
    if now.hour % 3 == 0 and now.minute == 0:
        try:
            if QUIZ_CHANNEL_ID is None:
                print("⚠️ QUIZ_CHANNEL_ID가 설정되지 않았습니다.")
                return
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, question, answer FROM quizzes 
                WHERE sent_to_discord = FALSE 
                ORDER BY created_at ASC 
                LIMIT 1
            ''')
            result = cursor.fetchone()
            if result:
                quiz_id, question, answer = result
                if QUIZ_CHANNEL_ID is not None:
                    channel = bot.get_channel(QUIZ_CHANNEL_ID)
                    if isinstance(channel, discord.TextChannel):
                        # 직접 question 사용 (파싱 불필요)
                        if question and question.strip():
                            await channel.send(f"\U0001F3AF **퀴즈 #{quiz_id}**\n{question}\n\n⏰ *2시간 후에 정답이 공개됩니다!*")
                            cursor.execute('''
                                UPDATE quizzes 
                                SET sent_to_discord = TRUE, quiz_sent_at = ? 
                                WHERE id = ?
                            ''', (get_kst_now(), quiz_id))
                            conn.commit()
                            print(f"✅ 퀴즈 ID {quiz_id} 전송 완료 (시간: {now.hour}시)")
                        else:
                            print(f"❌ 퀴즈 ID {quiz_id} 문제 내용이 비어있습니다.")
                    else:
                        print(f"❌ 채널을 찾을 수 없거나 텍스트 채널이 아닙니다.")
            conn.close()
        except Exception as e:
            print(f"❌ 퀴즈 전송 중 오류: {e}")

@tasks.loop(minutes=5)
async def check_and_send_answers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        two_hours_ago = get_kst_now() - timedelta(hours=2)
        cursor.execute('''
            SELECT id, question, answer FROM quizzes 
            WHERE sent_to_discord = TRUE 
            AND answer_sent = FALSE 
            AND quiz_sent_at IS NOT NULL 
            AND quiz_sent_at <= ?
            ORDER BY quiz_sent_at ASC
        ''', (two_hours_ago,))
        results = cursor.fetchall()
        for quiz_id, question, answer in results:
            if QUIZ_CHANNEL_ID is not None:
                channel = bot.get_channel(QUIZ_CHANNEL_ID)
                if isinstance(channel, discord.TextChannel):
                    # 직접 answer 사용 (파싱 불필요)
                    if answer and answer.strip():
                        await channel.send(f"\U0001F4A1 **퀴즈 #{quiz_id} 정답 공개!**\n{answer}")
                        cursor.execute('''
                            UPDATE quizzes 
                            SET answer_sent = TRUE, answer_sent_at = ? 
                            WHERE id = ?
                        ''', (get_kst_now(), quiz_id))
                        conn.commit()
                        print(f"✅ 퀴즈 ID {quiz_id} 정답 전송 완료")
                    else:
                        await channel.send(f"\U0001F4A1 **퀴즈 #{quiz_id} 정답 공개!**\n⚠️ 정답을 가져오는 중 문제가 발생했습니다.")
                        print(f"❌ 퀴즈 ID {quiz_id} 답변 내용이 비어있습니다.")
        conn.close()
    except Exception as e:
        print(f"❌ 답변 전송 중 오류: {e}")

@bot.tree.command(name="답", description="퀴즈의 답을 보여줍니다")
@app_commands.describe(quiz_id="특정 퀴즈 ID (생략시 최신 퀴즈)")
async def show_answer(interaction: discord.Interaction, quiz_id: Optional[int] = None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if quiz_id:
            cursor.execute('SELECT question, answer FROM quizzes WHERE id = ?', (quiz_id,))
        else:
            cursor.execute('''
                SELECT question, answer FROM quizzes 
                WHERE sent_to_discord = TRUE 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
        result = cursor.fetchone()
        if result:
            question, answer = result
            # 직접 answer 사용 (파싱 불필요)
            if answer and answer.strip():
                await interaction.response.send_message(f"\U0001F4A1 **정답:** {answer}")
            else:
                await interaction.response.send_message("⚠️ 정답을 가져오는 중 문제가 발생했습니다.")
        else:
            await interaction.response.send_message("❌ 정답을 찾을 수 없습니다.")
        conn.close()
    except Exception as e:
        await interaction.response.send_message(f"❌ 오류가 발생했습니다: {e}")

@bot.tree.command(name="퀴즈", description="수동으로 퀴즈를 요청합니다")
async def manual_quiz(interaction: discord.Interaction):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, question, answer FROM quizzes 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        result = cursor.fetchone()
        if result:
            quiz_id, question, answer = result
            # 직접 question 사용 (파싱 불필요)
            if question and question.strip():
                await interaction.response.send_message(f"\U0001F3AF **수동 퀴즈 #{quiz_id}**\n{question}")
            else:
                await interaction.response.send_message("⚠️ 퀴즈를 가져오는 중 문제가 발생했습니다.")
        else:
            await interaction.response.send_message("❌ 저장된 퀴즈가 없습니다.")
        conn.close()
    except Exception as e:
        await interaction.response.send_message(f"❌ 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    if BOT_TOKEN:
        bot.run(BOT_TOKEN)
    else:
        print("❌ BOT_TOKEN이 설정되지 않았습니다.")