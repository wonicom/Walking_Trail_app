import mysql.connector
import requests
import xml.etree.ElementTree as ET
from pyproj import Proj, Transformer
import time
from cachetools import TTLCache

# MySQL 설정
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "yourpassword",  # MySQL root 비밀번호 입력
    "database": "air_quality_db",
}

# MySQL 연결 함수
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# API 키
IQAIR_API_KEY = "API_KEY"

# 캐시 설정 (5분간 동일 좌표 요청 캐싱)
air_quality_cache = TTLCache(maxsize=100, ttl=300)

# IQAir API로 공기질 데이터 가져오기 및 MySQL에 저장
def fetch_and_store_air_quality(course_name, lat, lon):
    cache_key = (round(lat, 3), round(lon, 3))

    # 캐시 확인
    if cache_key in air_quality_cache:
        return air_quality_cache[cache_key]

    url = f"http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={IQAIR_API_KEY}"

    for attempt in range(3):  # 3번까지 재시도
        try:
            time.sleep(1)
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "success":
                aqius = data["data"]["current"]["pollution"]["aqius"]
                main_pollutant = data["data"]["current"]["pollution"]["mainus"]

                air_quality = {
                    "aqius": aqius,
                    "main_pollutant": main_pollutant
                }

                # MySQL에 저장
                conn = get_db_connection()
                cursor = conn.cursor()

                query = """
                INSERT INTO real_time_air_quality (course_name, lat, lon, aqius, main_pollutant, data_source)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                aqius = VALUES(aqius),
                main_pollutant = VALUES(main_pollutant),
                collected_at = CURRENT_TIMESTAMP;
                """

                cursor.execute(query, (course_name, lat, lon, aqius, main_pollutant, "IQAir"))
                conn.commit()

                cursor.close()
                conn.close()

                # 캐시 저장
                air_quality_cache[cache_key] = air_quality

                return air_quality

        except requests.exceptions.RequestException as e:
            if response.status_code == 429:
                print(f"⚠️ API 요청 초과(429) 발생. 10초 후 재시도... (시도 {attempt + 1}/3)")
                time.sleep(10)
            else:
                print(f"❌ API 요청 실패: {e}")
                break

    return None

# 테스트 실행
if __name__ == "__main__":
    sample_courses = [
        {"name": "hanriver", "lat": 37.570, "lon": 126.977},
        {"name": "namsan", "lat": 37.551, "lon": 126.988}
    ]

    for course in sample_courses:
        air_quality = fetch_and_store_air_quality(course["name"], course["lat"], course["lon"])
        if air_quality:
            print(f"🌫 {course['name']} - AQI: {air_quality['aqius']}, 주요 오염물질: {air_quality['main_pollutant']}")
