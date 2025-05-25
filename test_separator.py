#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
구분자 변경 테스트 스크립트
"""

from ai_quiz_functions import process_string_by_argument

def test_separator_change():
    """★ 구분자 테스트"""
    print("=" * 50)
    print("🧪 구분자 변경 테스트 (; → ★)")
    print("=" * 50)
    
    # 테스트 문자열 (새로운 ★ 구분자 사용)
    test_string = """오늘의 문제- 다음 중 Python에서 리스트를 정렬하는 메서드는?
a) sort()
b) order()
c) arrange()
d) organize()
★답: (a) sort()"""
    
    print(f"📝 테스트 문자열:")
    print(test_string)
    print("\n" + "─" * 50)
    
    # 문제 부분 추출 (매개변수 1)
    question_part = process_string_by_argument(test_string, '1')
    print(f"🎯 문제 부분 (매개변수 1):")
    print(question_part)
    print("\n" + "─" * 50)
    
    # 답 부분 추출 (매개변수 2)
    answer_part = process_string_by_argument(test_string, '2')
    print(f"💡 답 부분 (매개변수 2):")
    print(answer_part)
    print("\n" + "─" * 50)
    
    # 기존 ; 구분자로 테스트 (실패해야 정상)
    old_test_string = """오늘의 문제- 테스트;답: 테스트답"""
    print(f"🔄 기존 ; 구분자 테스트 (실패해야 정상):")
    print(f"입력: {old_test_string}")
    old_result = process_string_by_argument(old_test_string, '2')
    print(f"결과: {old_result}")
    
    print("\n" + "=" * 50)
    print("✅ 구분자 변경 테스트 완료!")
    print("=" * 50)

if __name__ == "__main__":
    test_separator_change()
