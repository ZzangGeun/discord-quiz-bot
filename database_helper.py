#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Railway용 데이터베이스 헬퍼
파일 기반 SQLite (프로세스 간 공유 가능)
"""

import sqlite3
import os
from datetime import datetime

# Railway 환경 감지
IS_RAILWAY = os.getenv('RAILWAY_ENVIRONMENT') is not None

# 데이터베이스 연결 설정
if IS_RAILWAY:
    # Railway: 임시 파일 기반 SQLite (프로세스 간 공유 가능)
    DB_PATH = '/tmp/quiz_database.db'
    print("🚂 Railway 환경: 임시 파일 기반 SQLite 사용 (/tmp/)")
else:
    # 로컬: 파일 기반 SQLite
    DB_PATH = 'quiz_database.db'
    print("💻 로컬 환경: 파일 기반 SQLite 사용")

def get_db_connection():
    """데이터베이스 연결 반환"""
    return sqlite3.connect(DB_PATH)

def init_database():
    """데이터베이스 초기화 (환경별 대응)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            question TEXT NULL,
            answer TEXT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_to_discord BOOLEAN DEFAULT FALSE,
            quiz_sent_at TIMESTAMP NULL,
            answer_sent BOOLEAN DEFAULT FALSE,
            answer_sent_at TIMESTAMP NULL
        )
    ''')
    
    # 기존 테이블에 새 컬럼들 추가
    columns_to_add = [
        ('question', 'TEXT NULL'),
        ('answer', 'TEXT NULL'),
        ('quiz_sent_at', 'TIMESTAMP NULL'),
        ('answer_sent', 'BOOLEAN DEFAULT FALSE'),
        ('answer_sent_at', 'TIMESTAMP NULL')
    ]
    
    for column_name, column_type in columns_to_add:
        try:
            cursor.execute(f'ALTER TABLE quizzes ADD COLUMN {column_name} {column_type}')
        except sqlite3.OperationalError:
            pass
    
    conn.commit()
    conn.close()
    
    if IS_RAILWAY:
        print("✅ Railway 임시 파일 DB 초기화 완료")
    else:
        print("✅ 로컬 파일 DB 초기화 완료")
