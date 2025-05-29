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
2) 너는 코딩테스트, 알고리즘, SQL등 테스트를 위해 문제를 출제하는 AI야 난이도는 컴퓨터공학과의 학부 졸업생이 20분 정도 고민해야 풀 수 있는 중상급 수준이어야 해.                                                                                                                                         
3) 선택한 학문과 관련해서 구글 검색을 이용해서 개념을 매우 상세히 학습 후 다양한 문제를 출제하면 돼.
4) 문제 중 코딩테스트의 경우는 파이썬으로 내거나 C언어로 내줘. 복잡한 알고리즘, 자료구조, 시간복잡도 모두 고려하여 다양한 문제를 출제해줘.                                                                                                                             
5) 학습한 개념을 가지고 객관식 또는 주관식 문제를 1문제만 문제와 답을 출력 하는데 문제의 답 앞에는 반드시 ★을 넣어 문제와 답을 구분하기 위한 구분자로 사용할거야. 문제는 단순 암기보다는 깊은 이해와 응용이 필요한 수준으로 출제해줘.                                                                                                                                                 
주의사항) 
- 절대로 순서대로 문제를 출제하지마. 출제할 개념의 순서는 랜덤으로 가지고 와야해.
- 반드시 ★ 기호를 답 앞에 포함해야 해. 이는 필수 요구사항이야.
- ★ 기호는 정확히 "★답:" 형태로 작성해야 해.

3. 표현                                                                                                                                                                                               
- 너의 응답 양식은 다음과 같아.                                                                                                                                                                       
오늘의 문제- (문제)                                                                                                                                                                                   
a)

b)

c)

d)

★답: (답)                                                                                                                                                                                             

4. 예시(객관식 문제)                                                                                                                                                                                               
오늘의 문제- 다음 중 이진 탐색 트리에서 특정 값 k보다 작은 모든 노드의 개수를 O(log n) 시간 복잡도로 구하기 위해 각 노드에 추가로 저장해야 하는 정보는?                                                                                                                                      
- a) 왼쪽 서브트리의 노드 개수

- b) 오른쪽 서브트리의 노드 개수

- c) 자신을 루트로 하는 서브트리의 전체 노드 개수

- d) 부모 노드에 대한 포인터                                                                                                                                                                            
★답: (c)

5. 예시(주관식 문제)
동적 계획법을 사용하여 0-1 배낭 문제를 해결하는 파이썬 함수로 작성하세요. 
가방의 용량은 W, 물건들의 무게는 weights 리스트, 가치는 values 리스트로 주어집니다.

★답:
1. 파이썬 : 
def knapsack(W, weights, values, n):
    dp = [[0 for _ in range(W + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, W + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(values[i-1] + dp[i-1][w-weights[i-1]], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]
    return dp[n][W]

"""


def generate_quiz():
    """퀴즈를 생성하고 데이터베이스에 저장"""
    max_retries = 5

    for attempt in range(max_retries):
        try:
            print(f"[{datetime.now()}] 새로운 퀴즈를 생성 중... (시도 {attempt + 1}/{max_retries})")
            print(f"🗄️ 데이터베이스 모드: {'메모리 (Railway)' if IS_RAILWAY else '파일 (로컬)'}")

            # Gemini chat API 호출
            response = client.models.chat(
                contents=[{"role": "user", "parts": [query_text]}],
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1500,
                }
            )

            if not response:
                print(f"❌ 시도 {attempt + 1}: 응답이 None입니다.")
                continue

            # 텍스트 추출
            quiz_content = None
            if hasattr(response, 'text') and response.text:
                quiz_content = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                quiz_content = response.candidates[0].content.parts[0].text.strip()

            if not quiz_content:
                print(f"❌ 시도 {attempt + 1}: 생성된 퀴즈 내용이 비어있습니다.")
                continue

            # ★답: 패턴 확인
            if not re.search(r"★\s*답\s*:", quiz_content):
                print(f"❌ 시도 {attempt + 1}: '★답:' 형식이 올바르지 않습니다.")
                print("🔍 생성된 응답:\n", quiz_content)
                continue

            print(f"✅ 시도 {attempt + 1}에서 성공!")
            break

        except Exception as e:
            print(f"❌ 시도 {attempt + 1} 실패: {e}")
            if attempt == max_retries - 1:
                print("❌ 모든 재시도 실패. 나중에 다시 시도하세요.")
                return
            time.sleep(5)  # 재시도 전 대기

    else:
        print("❌ 모든 시도에서 유효한 응답을 받지 못했습니다.")
        return

    # DB 저장
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO quizzes (content) VALUES (?)',
            (quiz_content,)
        )

        if not IS_RAILWAY:
            conn.commit()
            conn.close()
        else:
            conn.commit()

        quiz_id = cursor.lastrowid

        print(f"✅ 퀴즈 ID {quiz_id} 생성 완료!")
        print(f"📝 내용 미리보기: {quiz_content[:100]}...")

        # 로컬 파일 백업
        try:
            with open("cote_bot.txt", "a", encoding="utf-8") as file:
                file.write(f"\n[{datetime.now()}] Quiz ID: {quiz_id}\n")
                file.write(quiz_content)
                file.write("\n" + "=" * 50 + "\n")
        except Exception as file_error:
            print(f"⚠️ 파일 백업 실패 (Railway에서는 정상): {file_error}")

    except Exception as e:
        print(f"❌ 데이터베이스 저장 중 오류: {e}")
        import traceback
        traceback.print_exc()


def run_scheduler():
    """스케줄러 실행"""
    print("🕐 퀴즈 생성 스케줄러를 시작합니다...")
    print("📅 30분마다 새로운 퀴즈가 생성됩니다.")
    
    # 데이터베이스 초기화
    init_database()
    
    
    # 첫 번째 퀴즈 즉시 생성
    generate_quiz()

    # 30분마다 퀴즈 생성 스케줄
    schedule.every(30).minutes.do(generate_quiz)

    # 스케줄러 실행
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    run_scheduler()
