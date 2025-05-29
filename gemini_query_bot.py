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
4) 문제 중 코딩테스트의 경우는 파이썬 또는 C 두개의 문법을 사용하는데 두개의 문법을 사용 하면 선지에도 파이썬과 C가 같은 결과 값을 출력하도록 하거나 작성 코드에 빈칸을 넣어 선지로 선택할 수 있도록 해줘. 복잡한 알고리즘, 자료구조, 시간복잡도 분석이 필요한 문제를 출제해줘.                                                                                                                             
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
동적 계획법을 사용하여 0-1 배낭 문제를 해결하는 파이썬 함수 또는 C 함수로 작성하세요. 
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

2. C언어:
#include <stdio.h>

int knapsack(int W, int weights[], int values[], int n) {
    int dp[n+1][W+1];

    // 초기화
    for (int i = 0; i <= n; i++) {
        for (int w = 0; w <= W; w++) {
            dp[i][w] = 0;
        }
    }

    // DP 테이블 채우기
    for (int i = 1; i <= n; i++) {
        for (int w = 1; w <= W; w++) {
            if (weights[i-1] <= w) {
                int include = values[i-1] + dp[i-1][w - weights[i-1]];
                int exclude = dp[i-1][w];
                dp[i][w] = (include > exclude) ? include : exclude;
            } else {
                dp[i][w] = dp[i-1][w];
            }
        }
    }

    return dp[n][W];
}
"""


def generate_quiz():
    """퀴즈를 생성하고 데이터베이스에 저장"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"[{datetime.now()}] 새로운 퀴즈를 생성 중... (시도 {attempt + 1}/{max_retries})")
            print(f"🗄️ 데이터베이스 모드: {'메모리 (Railway)' if IS_RAILWAY else '파일 (로컬)'}")
            
            # 제미나이 설정 - 더 간단한 방식으로 호출
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=query_text,  # 더 간단한 방식
                config=types.GenerateContentConfig(
                    temperature=1.3,
                    max_output_tokens=2000,
                )
            )

            # API 응답 상세 검증 및 디버깅
            print(f"🔍 디버그: response 타입: {type(response)}")
            print(f"🔍 디버그: response 속성: {dir(response) if response else 'None'}")
            
            if response is None:
                print(f"❌ 시도 {attempt + 1}: response가 None입니다.")
                continue
            
            # candidates 속성을 통해 접근 시도
            quiz_content = None
            try:
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            quiz_content = candidate.content.parts[0].text
                elif hasattr(response, 'text'):
                    quiz_content = response.text
                else:
                    print(f"🔍 디버그: response 구조를 파악할 수 없습니다.")
                    print(f"🔍 디버그: response 내용: {response}")
                    continue
            except Exception as parse_error:
                print(f"❌ 응답 파싱 오류: {parse_error}")
                continue
                
            if not quiz_content:
                print(f"❌ 시도 {attempt + 1}: 생성된 퀴즈 내용이 비어있습니다.")
                continue
            
            quiz_content = quiz_content.strip()
              # 빈 내용 체크
            if not quiz_content:
                print(f"❌ 시도 {attempt + 1}: 퀴즈 내용이 공백입니다.")
                continue
            
            # ★ 구분자 검증
            if '★' not in quiz_content:
                print(f"❌ 시도 {attempt + 1}: 퀴즈에 ★ 구분자가 없습니다.")
                print(f"🔍 생성된 내용: {quiz_content[:200]}...")
                continue
            
            # ★답: 형식 검증
            if '★답:' not in quiz_content and '★답 :' not in quiz_content:
                print(f"❌ 시도 {attempt + 1}: '★답:' 형식이 올바르지 않습니다.")
                print(f"🔍 생성된 내용: {quiz_content[:200]}...")
                continue
            
            # 성공적으로 응답을 받았으면 나머지 로직 실행
            print(f"✅ 시도 {attempt + 1}에서 성공!")
            break
            
        except Exception as e:
            print(f"❌ 시도 {attempt + 1} 실패: {e}")
            if attempt == max_retries - 1:
                print("❌ 모든 재시도 실패. 나중에 다시 시도하세요.")
                return
            time.sleep(5)  # 재시도 전 5초 대기
    
    else:
        print("❌ 모든 시도에서 유효한 응답을 받지 못했습니다.")
        return

    # 나머지 데이터베이스 저장 로직은 그대로...
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
        
        # 파일 백업 저장
        try:
            with open("cote_bot.txt", "a", encoding="utf-8") as file:
                file.write(f"\n[{datetime.now()}] Quiz ID: {quiz_id}\n")
                file.write(quiz_content)
                file.write("\n" + "="*50 + "\n")
        except Exception as file_error:
            print(f"⚠️ 파일 백업 실패 (Railway에서는 정상): {file_error}")
            
    except Exception as e:
        print(f"❌ 데이터베이스 저장 중 오류: {e}")
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
