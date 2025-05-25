"""
30분 답변 시스템 테스트용 스크립트
실제로는 30분이지만 테스트를 위해 30초로 설정
"""
import sqlite3
from datetime import datetime, timedelta

def test_answer_timing():
    """답변 타이밍 시스템 테스트"""
    conn = sqlite3.connect('quiz_database.db')
    cursor = conn.cursor()
    
    # 현재 퀴즈 상태 확인
    cursor.execute('''
        SELECT id, content, sent_to_discord, quiz_sent_at, answer_sent 
        FROM quizzes 
        ORDER BY created_at DESC 
        LIMIT 5
    ''')
    
    results = cursor.fetchall()
    print("📊 현재 퀴즈 상태:")
    print("ID | 전송됨 | 퀴즈전송시간 | 답변전송됨")
    print("-" * 50)
    
    for quiz_id, content, sent, quiz_sent_at, answer_sent in results:
        quiz_part = content.split(';')[0][:30] + "..." if len(content.split(';')[0]) > 30 else content.split(';')[0]
        print(f"{quiz_id:2d} | {sent:6} | {quiz_sent_at or 'None':16} | {answer_sent}")
        
    # 30분 지난 퀴즈 찾기 (테스트용으로 30초로 변경)
    thirty_seconds_ago = datetime.now() - timedelta(seconds=30)  # 테스트용
    print(f"\n🔍 30초 전 시간: {thirty_seconds_ago}")
    
    cursor.execute('''
        SELECT id, content FROM quizzes 
        WHERE sent_to_discord = TRUE 
        AND answer_sent = FALSE 
        AND quiz_sent_at IS NOT NULL 
        AND quiz_sent_at <= ?
        ORDER BY quiz_sent_at ASC
    ''', (thirty_seconds_ago,))
    
    ready_for_answer = cursor.fetchall()
    print(f"\n✅ 답변 준비된 퀴즈: {len(ready_for_answer)}개")
    
    for quiz_id, content in ready_for_answer:
        answer = content.split(';')[1] if ';' in content else "답변 없음"
        print(f"  - 퀴즈 #{quiz_id}: {answer}")
    
    conn.close()

if __name__ == "__main__":
    test_answer_timing()
