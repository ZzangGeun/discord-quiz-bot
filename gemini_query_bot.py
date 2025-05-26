from google import genai         
from google.genai import types 
import sqlite3
import schedule
import time
from datetime import datetime
from config import GEMINI_API_KEY
from database_helper import get_db_connection, init_database, IS_RAILWAY

# 환경변수에서 API 키 가져오기
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경변수를 설정해주세요!")

client = genai.Client(api_key=GEMINI_API_KEY)

#제미나이한테 보낼 text 작성
query_text = """
1.  페르소나 :                                                                                                                                                                                        

2. 작업                                                                                                                                                                                               
1) 너는 대답하지말고 바로 문제를 출제하면 돼.
2) 너는 코딩테스트, 알고리즘, SQL등 테스트를 위해 문제를 출제하는 AI야 난이도는 컴퓨터공학과의 학부 졸업생이 눈으로 10분 안에 풀 정도면 돼.                                                                                                                                         
3) 선택한 학문과 관련해서 구글 검색을 이용해서 개념을 매우 상세히 학습 후 다양한 문제를 출제하면 돼.
4) 문제 중 코딩테스트의 경우는 파이썬 기준으로 작성을 하고 선지에는 결과 값을 넣거나 작성 코드에 빈칸을 넣어 선지로 선택할 수 있도록 해줘.                                                                                                                             
5) 학습한 개념을 가지고 객관식 또는 주관식 문제를 1문제만 문제와 답을 출력 하는데 답 앞에는 반드시 ★을 넣어 문제와 답을 구분하기 위한 구분자로 사용할거야.                                                                                                                                                 
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

4. 예시(객관식 문제)                                                                                                                                                                                               
오늘의 문제- 다음 중 SQL DML에서 데이터를 삭제하는 명령어는 무엇인가요?                                                                                                                                      
- a) SELECT

- b) INSERT

- c) UPDATE

- d) DELETE                                                                                                                                                                            
★답: (d)

5. 예시(주관식 문제)
파이썬에서 리스트의 모든 요소를 제곱하는 함수를 작성하세요.

★답: (def square_elements(lst): return [x**2 for x in lst])
"""

# init_database 함수는 database_helper에서 import됨

def generate_quiz():
    """퀴즈를 생성하고 데이터베이스에 저장"""
    try:
        print(f"[{datetime.now()}] 새로운 퀴즈를 생성 중...")
        print(f"🗄️ 데이터베이스 모드: {'메모리 (Railway)' if IS_RAILWAY else '파일 (로컬)'}")
        
        #제미나이 설정
        response = client.models.generate_content(                                                                                                                                                             
            model="gemini-2.5-flash-preview-04-17", contents=query_text,                                                                                                                                       
            config=types.GenerateContentConfig(                                                                                                                                                                
                temperature=1.5,
                max_output_tokens=1500,  # 최대 출력 토큰 수                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
            )                                                                                                                                                                                                  
        )
        
        # API 응답 검증
        if response is None or response.text is None:
            print("❌ Gemini API에서 빈 응답을 받았습니다. 다시 시도합니다...")
            return
            
        quiz_content = response.text.strip()
        
        # 빈 내용 체크
        if not quiz_content:
            print("❌ 생성된 퀴즈 내용이 비어있습니다.")
            return
        
        # 데이터베이스에 저장
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO quizzes (content) VALUES (?)',
            (quiz_content,)
        )
        
        # Railway가 아닌 경우에만 commit과 close
        if not IS_RAILWAY:
            conn.commit()
            conn.close()
        else:
            conn.commit()  # 메모리 DB도 commit은 필요
        
        quiz_id = cursor.lastrowid
        
        print(f"✅ 퀴즈 ID {quiz_id} 생성 완료!")
        print(f"📝 내용 미리보기: {quiz_content[:100]}...")
        
        # 파일 백업 저장 (Railway에서도 임시로 저장)
        try:
            with open("cote_bot.txt", "a", encoding="utf-8") as file:
                file.write(f"\n[{datetime.now()}] Quiz ID: {quiz_id}\n")
                file.write(quiz_content)
                file.write("\n" + "="*50 + "\n")
        except Exception as file_error:
            print(f"⚠️ 파일 백업 실패 (Railway에서는 정상): {file_error}")
            
    except Exception as e:
        print(f"❌ 퀴즈 생성 중 오류: {e}")
        import traceback
        traceback.print_exc()

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
        time.sleep(600)  # 10분마다 체크

if __name__ == "__main__":
    run_scheduler()
