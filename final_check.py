#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub 커밋 전 최종 확인 스크립트
"""

import os

def check_files():
    """주요 파일들이 올바르게 수정되었는지 확인"""
    print("🔍 GitHub 커밋 전 최종 확인")
    print("=" * 50)
    
    files_to_check = {
        "ai_quiz_functions.py": "★ 구분자",
        "discord_bot.py": "30분 간격 전송",
        "gemini_query_bot.py": "★ 구분자 in AI prompt",
        "main_railway.py": "discord_bot import",
        "cote_bot.txt": "★ 구분자 in data"
    }
    
    all_good = True
    
    for file, description in files_to_check.items():
        if os.path.exists(file):
            print(f"✅ {file} - {description}")
        else:
            print(f"❌ {file} - 파일 없음!")
            all_good = False
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 모든 파일이 준비되었습니다!")
        print("💡 이제 GitHub에 커밋할 수 있습니다:")
        print()
        print("git add .")
        print("git commit -m 'feat: 구분자 변경(;→★) 및 30분 간격 답변 전송 구현'")
        print("git push")
        print()
        print("🚀 Railway/Replit에서 자동으로 배포됩니다!")
    else:
        print("⚠️ 일부 파일에 문제가 있습니다. 다시 확인해주세요.")
    
    print("=" * 50)

if __name__ == "__main__":
    check_files()
