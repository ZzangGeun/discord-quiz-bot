#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Railway용 데이터베이스 헬퍼
메모리 기반 SQLite + 파일 백업 시스템
"""

import sqlite3
import os
from datetime import datetime

# Railway 환경 감지
IS_RAILWAY = os.getenv('RAILWAY_ENVIRONMENT') is not None

# 데이터베이스 연결 설정
if IS_RAILWAY:
    # Railway: 메모리 기반 SQLite
    DB_PATH = ':memory:'
    print("🚂 Railway 환경: 메모리 기반 SQLite 사용")
else:
    # 로컬: 파일 기반 SQLite
    DB_PATH = 'quiz_database.db'
    print("💻 로컬 환경: 파일 기반 SQLite 사용")

# 메모리 데이터베이스 (Railway용)
_memory_db = None

def get_db_connection():
    """데이터베이스 연결 반환"""
    global _memory_db
    
    if IS_RAILWAY:
        # Railway: 메모리 DB 재사용
        if _memory_db is None:
            _memory_db = sqlite3.connect(':memory:', check_same_thread=False)
            init_memory_db(_memory_db)
        return _memory_db
    else:
        # 로컬: 파일 DB
        return sqlite3.connect(DB_PATH)

def init_memory_db(conn):
    """메모리 데이터베이스 초기화"""
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
    conn.commit()
    print("✅ 메모리 데이터베이스 초기화 완료")

def init_database():
    """데이터베이스 초기화 (환경별 대응)"""
    if IS_RAILWAY:
        # Railway: 메모리 DB는 get_db_connection에서 자동 초기화
        print("🚂 Railway 메모리 DB 준비 완료")
    else:
        # 로컬: 파일 DB 초기화
        conn = sqlite3.connect(DB_PATH)
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
        
        # 기존 테이블에 컬럼이 없다면 추가
        try:
            cursor.execute('ALTER TABLE quizzes ADD COLUMN quiz_sent_at TIMESTAMP NULL')
        except sqlite3.OperationalError:
            pass
        
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
        print("✅ 로컬 파일 DB 초기화 완료")
