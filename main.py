import requests  # requests 모듈 임포트
import xml.etree.ElementTree as ET  # ET 모듈 임포트
from pyproj import Proj, transform
from functools import lru_cache

# API 키 설정
SEOUL_API_KEY = "57665a72576330393834646b496a75"
IQAIR_API_KEY = "7aa890fa-64df-4bea-9a25-9647060415d8"

# 1. 좌표 변환 함수 (GRS80TM -> WGS84)
def convert_grs80_to_wgs84(x, y):
    grs80 = Proj(proj='tmerc', lat_0=38, lon_0=127.5, k=1.0, x_0=200000, y_0=500000, ellps='GRS80', units='m')
    wgs84 = Proj(proj='latlong', datum='WGS84')
    lon, lat = transform(grs80, wgs84, x, y)
    return lat, lon

# 2. 서울시 산책로 데이터 가져오기
def fetch_walk_courses():
    url = f"http://openAPI.seoul.go.kr:8088/{SEOUL_API_KEY}/xml/SeoulGilWalkCourse/1/10"
    response = requests.get(url)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    walk_courses = []
    for row in root.findall(".//row"):
        name = row.find("COURSE_NAME").text
        x = float(row.find("X").text)
        y = float(row.find("Y").text)
        distance = row.find("DISTANCE").text
        lead_time = row.find("LEAD_TIME").text

        # 좌표 변환 (GRS80TM -> WGS84)
        lat, lon = convert_grs80_to_wgs84(x, y)
        walk_courses.append({"name": name, "lat": lat, "lon": lon, "distance": distance, "lead_time": lead_time})

    return walk_courses

# 3. 공기질 데이터 가져오기 (IQAir API)

@lru_cache(maxsize=100)
def fetch_air_quality(lat, lon):
    url = f"http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={IQAIR_API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if data["status"] == "success":
        return {
            "aqius": data["data"]["current"]["pollution"]["aqius"],
            "main_pollutant": data["data"]["current"]["pollution"]["mainus"]
        }
    else:
        raise Exception("공기질 데이터를 가져오지 못했습니다.")

# 4. 공기질 평가 함수
def evaluate_air_quality(aqius):
    if aqius <= 50:
        return "양호"
    elif aqius <= 100:
        return "보통"
    elif aqius <= 150:
        return "민감군에 나쁨"
    elif aqius <= 200:
        return "나쁨"
    elif aqius <= 300:
        return "매우 나쁨"
    else:
        return "위험"

# 5. 산책로 추천 로직
def recommend_walk_courses(user_lat, user_lon):
    courses = fetch_walk_courses()  # 서울시 산책로 데이터 가져오기
    recommendations = []

    for course in courses:
        try:
            # 각 산책로의 공기질 데이터 가져오기
            air_quality = fetch_air_quality(course["lat"], course["lon"])
            aqius = air_quality["aqius"]

            # AQI 기준으로 추천
            if aqius <= 100:  # 공기질 지수 100 이하만 추천
                recommendations.append({
                    "name": course["name"],
                    "distance": course["distance"],
                    "lead_time": course["lead_time"],
                    "aqi": aqius,
                    "air_quality": evaluate_air_quality(aqius),
                    "main_pollutant": air_quality["main_pollutant"]
                })
        except Exception as e:
            print(f"{course['name']} 산책로에서 오류 발생: {e}")

    return recommendations

# 6. 실행 및 결과 출력
if __name__ == "__main__":
    try:
        # 사용자 위치 (예: 서울 시청)
        user_lat, user_lon = 37.5665, 126.9780

        # 추천 산책로 가져오기
        recommendations = recommend_walk_courses(user_lat, user_lon)

        # 결과 출력
        for rec in recommendations:
            print(f"산책로: {rec['name']}")
            print(f"거리: {rec['distance']} km, 예상 소요 시간: {rec['lead_time']} 분")
            print(f"AQI: {rec['aqi']}, 공기질 상태: {rec['air_quality']}")
            print(f"주요 오염물질: {rec['main_pollutant']}")
            print("-" * 30)
    except Exception as e:
        print(f"오류 발생: {e}")
