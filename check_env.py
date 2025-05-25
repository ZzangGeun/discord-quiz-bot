import os
from config import BOT_TOKEN, QUIZ_CHANNEL_ID, GEMINI_API_KEY

def check_environment():
    """환경 변수 확인 스크립트"""
    print("=" * 50)
    print("🔍 환경 변수 확인")
    print("=" * 50)
    
    configs = {
        'BOT_TOKEN': BOT_TOKEN,
        'QUIZ_CHANNEL_ID': QUIZ_CHANNEL_ID,
        'GEMINI_API_KEY': GEMINI_API_KEY
    }
    
    all_set = True
    
    for var, value in configs.items():
        if value:
            if var == 'BOT_TOKEN':
                print(f"✅ {var}: {str(value)[:20]}..." if len(str(value)) > 20 else f"✅ {var}: {value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 설정되지 않음")
            all_set = False
    
    print("=" * 50)
    
    if all_set:
        print("🎉 모든 환경 변수가 올바르게 설정되었습니다!")
        print("🚀 이제 main_replit.py를 실행할 수 있습니다.")
    else:
        print("⚠️  일부 환경 변수가 설정되지 않았습니다.")
        print("🔧 Replit Secrets에서 다음을 확인해주세요:")
        print("   - BOT_TOKEN (Discord 봇 토큰)")
        print("   - QUIZ_CHANNEL_ID (Discord 채널 ID)")
        print("   - GEMINI_API_KEY (Google Gemini API 키)")
    
    print("=" * 50)
    return all_set

if __name__ == "__main__":
    check_environment()
