import mysql.connector

# MySQL 데이터베이스 연결
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",  # MySQL 비밀번호 입력
    database="air_quality_db"
)
cursor = conn.cursor()

# /search 테이블 생성
cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_info (
        search_id INT PRIMARY KEY AUTO_INCREMENT,
        course_name VARCHAR(255),
        aqi INT,
        pm25 FLOAT,
        pm10 FLOAT,
        o3 FLOAT,
        timestamp DATETIME,
        data_source VARCHAR(255)
    )
""")

# /average 테이블 생성
cursor.execute("""
    CREATE TABLE IF NOT EXISTS average_air_quality (
        avg_id INT PRIMARY KEY AUTO_INCREMENT,
        course_name VARCHAR(255),
        average_aqi FLOAT,
        average_pm25 FLOAT,
        average_pm10 FLOAT,
        average_o3 FLOAT,
        time_range VARCHAR(50),
        recommend_score FLOAT,
        data_source VARCHAR(255),
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# Users 테이블 생성
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100),
        location VARCHAR(255),
        preferred_route VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Trails 테이블 생성
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Trails (
        trail_id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(225),
        location VARCHAR(255),
        latitude FLOAT,
        longitude FLOAT,
        length_km FLOAT,
        difficulty VARCHAR(50),
        description TEXT,
        amenities JSON
    )
""")

# AirQuality 테이블 생성
cursor.execute("""
    CREATE TABLE IF NOT EXISTS AirQuality (
        aq_id INT PRIMARY KEY AUTO_INCREMENT,
        location_id INT,
        aqi INT,
        pm25 FLOAT,
        pm10 FLOAT,
        o3 FLOAT,
        timestamp DATETIME,
        FOREIGN KEY (location_id) REFERENCES Trails(trail_id)
    )
""")

# Recommendations 테이블 생성
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Recommendations (
        rec_id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT,
        trail_id INT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (trail_id) REFERENCES Trails(trail_id)
    )
""")

# 변경 사항 저장 및 연결 종료
conn.commit()
cursor.close()
conn.close()

print("모든 테이블이 성공적으로 생성되었습니다.")
