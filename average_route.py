import mysql.connector
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# MySQL 데이터베이스 연결
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="air_quality_db"
)
cursor = conn.cursor()

# 1. search_info 테이블 (특정 시간대의 공기질 조회)
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

# 2. average_air_quality 테이블 (산책로별 평균 공기질 정보)
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

conn.commit()
cursor.close()
conn.close()

print("모든 테이블이 성공적으로 생성되었습니다.")


# 3. 산책로 공기질 평균 API 구현
@app.route('/average', methods=['GET'])
def get_average_air_quality():
    course_name = request.args.get('course_name')

    if not course_name:
        return jsonify({"error": "course_name parameter is required"}), 400

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpassword",
        database="air_quality_db"
    )
    cursor = conn.cursor(dictionary=True)

    # 평균 AQI 및 PM2.5 조회
    query = """
        SELECT course_name, AVG(aqi) AS average_aqi, AVG(pm25) AS average_pm25,
               AVG(pm10) AS average_pm10, AVG(o3) AS average_o3, 
               '09:00-18:00' AS time_range, 75.0 AS recommend_score, 
               'IQAir, Seoul Open Data Plaza' AS data_source,
               NOW() AS last_updated
        FROM AirQuality
        JOIN Trails ON AirQuality.location_id = Trails.trail_id
        WHERE Trails.name = %s
        GROUP BY Trails.name
    """

    cursor.execute(query, (course_name,))
    result = cursor.fetchone()

    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "No data found for the given course name"}), 404


if __name__ == '__main__':
    app.run(debug=True)