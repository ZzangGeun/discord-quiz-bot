from google import genai         
from google.genai import types 
import sqlite3
import schedule
import time
from datetime import datetime
from config import GEMINI_API_KEY

# 환경변수에서 API 키 가져오기
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경변수를 설정해주세요!")

client = genai.Client(api_key=GEMINI_API_KEY)

#제미나이한테 보낼 text 작성
query_text = """
1.  페르소나 :                                                                                                                                                                                        

2. 작업                                                                                                                                                                                               
1) 너는 대답하지말고 바로 문제를 출제하면 돼.
2) 너는 코딩테스트, 알고리즘, SQL등 테스트를 위해 문제를 출제하는 AI야.                                                                                                                                         
3) 선택한 학문과 관련해서 구글 검색을 이용해서 개념을 매우 상세히 학습 후 다양한 문제를 출제하면 돼.
4) 문제 중 코딩테스트의 경우는 파이썬 기준으로 작성을 하고 선지에는 결과 값을 넣거나 작성 코드에 빈칸을 넣어 선지로 선택할 수 있도록 해줘.                                                                                                                             
5) 학습한 개념을 가지고 객관식 문제를 1문제만 출제해.                                                                                                                                                 
주의) 절대로 순서대로 문제를 출제하지마. 출제할 개념의 순서는 랜덤으로 가지고 와야해.                                                                                                                 

3. 표현                                                                                                                                                                                               
- 너의 응답 양식은 다음과 같아.                                                                                                                                                                       
오늘의 문제- (문제)                                                                                                                                                                                   
a)                                                                                                                                                                                                    
b)                                                                                                                                                                                                    
c)                                                                                                                                                                                                    
d)                                                                                                                                                                                                    
★답: (답)                                                                                                                                                                                             
주의) ★는 선지와 답을 구분해주기 위한 구분자야.

4. 예시                                                                                                                                                                                               
오늘의 문제- 다음 중 SQL DML에서 데이터를 삭제하는 명령어는 무엇인가요?                                                                                                                                      
- a) SELECT                                                                                                                                                                   
- b) INSERT                                                                                                                                                             
- c) UPDATE                                                                                                                                                          
- d) DELETE                                                                                                                                                                            
★답: (d)
"""

def init_database():
    """데이터베이스 초기화"""
    conn = sqlite3.connect('quiz_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_to_discord BOOLEAN DEFAULT FALSE,
            quiz_sent_at TIMESTAMP NULL,
            answer_sent BOOLEAN DEFAULT FALSE,
            answer_sent_at TIMESTAMP NULL
        )
    ''')
    
    # 기존 테이블에 새 컬럼 추가 (이미 존재하는 경우 무시)
    try:
        cursor.execute('ALTER TABLE quizzes ADD COLUMN quiz_sent_at TIMESTAMP NULL')
    except sqlite3.OperationalError:
        pass  # 컬럼이 이미 존재함
    
    try:
        cursor.execute('ALTER TABLE quizzes ADD COLUMN answer_sent BOOLEAN DEFAULT FALSE')
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute('ALTER TABLE quizzes ADD COLUMN answer_sent_at TIMESTAMP NULL')
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()

def generate_quiz():
    """퀴즈를 생성하고 데이터베이스에 저장"""
    try:
        print(f"[{datetime.now()}] 새로운 퀴즈를 생성 중...")
        
        #제미나이 설정
        response = client.models.generate_content(                                                                                                                                                             
            model="gemini-2.5-flash-preview-04-17", contents=query_text,                                                                                                                                       
            config=types.GenerateContentConfig(                                                                                                                                                                
                temperature=1.7                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
            )                                                                                                                                                                                                  
        )
        
        quiz_content = response.text.strip() if response.text else ""
        
        if not quiz_content:
            print("❌ Gemini API에서 빈 응답을 받았습니다.")
            return
        
        # 데이터베이스에 저장
        conn = sqlite3.connect('quiz_database.db')
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO quizzes (content) VALUES (?)',
            (quiz_content,)
        )
        
        conn.commit()
        quiz_id = cursor.lastrowid
        conn.close()
        
        print(f"✅ 퀴즈 ID {quiz_id} 생성 완료!")
        print(f"📝 내용 미리보기: {quiz_content[:100]}...")
        
        # 파일에도 백업 저장
        with open("cote_bot.txt", "a", encoding="utf-8") as file:
            file.write(f"\n[{datetime.now()}] Quiz ID: {quiz_id}\n")
            file.write(quiz_content)
            file.write("\n" + "="*50 + "\n")
            
    except Exception as e:
        print(f"❌ 퀴즈 생성 중 오류: {e}")

def run_scheduler():
    """스케줄러 실행"""
    print("🕐 퀴즈 생성 스케줄러를 시작합니다...")
    print("📅 1시간마다 새로운 퀴즈가 생성됩니다.")
    
    # 데이터베이스 초기화
    init_database()
    
    # 첫 번째 퀴즈 즉시 생성
    generate_quiz()
    
    # 1시간마다 퀴즈 생성 스케줄
    schedule.every(1).hours.do(generate_quiz)
    
    # 스케줄러 실행
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    run_scheduler()
