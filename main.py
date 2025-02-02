import requests
import xml.etree.ElementTree as ET
from pyproj import Proj, Transformer
import time
from cachetools import TTLCache

# API 키 설정
SEOUL_API_KEY = "57665a72576330393834646b496a75"
IQAIR_API_KEY = "7aa890fa-64df-4bea-9a25-9647060415d8"

# API 요청 횟수 제한
API_REQUEST_LIMIT = 10
api_request_count = 0

# TTL 캐시 적용 (5분 동안 동일 좌표 요청 캐싱)
air_quality_cache = TTLCache(maxsize=100, ttl=300)

# 좌표 변환 함수 (GRS80TM -> WGS84)
def convert_grs80_to_wgs84(x, y):
    transformer = Transformer.from_proj(
        Proj(proj='tmerc', lat_0=38, lon_0=127.5, k=1.0, x_0=200000, y_0=500000, ellps='GRS80', units='m'),
        Proj(proj='latlong', datum='WGS84'),
        always_xy=True
    )
    lon, lat = transformer.transform(x, y)
    return lat, lon

# 서울시 산책로 데이터 가져오기
def fetch_walk_courses():
    url = f"http://openAPI.seoul.go.kr:8088/{SEOUL_API_KEY}/xml/SeoulGilWalkCourse/1/10"
    response = requests.get(url)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    walk_courses = []
    seen_courses = set()  # 중복 방지를 위한 set

    for row in root.findall(".//row"):
        name = row.find("COURSE_NAME").text
        if name in seen_courses:  # 중복된 산책로인지 확인
            continue

        x = float(row.find("X").text)
        y = float(row.find("Y").text)
        distance = row.find("DISTANCE").text
        lead_time = row.find("LEAD_TIME").text

        # 좌표 변환 (GRS80TM -> WGS84)
        lat, lon = convert_grs80_to_wgs84(x, y)
        walk_courses.append({"name": name, "lat": lat, "lon": lon, "distance": distance, "lead_time": lead_time})

        seen_courses.add(name)  # 중복 방지를 위해 추가

    return walk_courses

# 공기질 데이터 가져오기 (IQAir API)
def fetch_air_quality(lat, lon):
    global api_request_count

    # API 요청 횟수 제한 확인
    if api_request_count >= API_REQUEST_LIMIT:
        print("⚠️ API 요청 횟수 초과! 추가 요청을 차단합니다.")
        return None

    # 캐시 확인 (반올림된 좌표로 캐싱)
    cache_key = (round(lat, 3), round(lon, 3))
    if cache_key in air_quality_cache:
        return air_quality_cache[cache_key]

    url = f"http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={IQAIR_API_KEY}"

    for attempt in range(3):  # 3번까지 재시도
        try:
            # 요청 간 간격을 두기 위해 1초 대기
            time.sleep(1)

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "success":
                air_quality = {
                    "aqius": data["data"]["current"]["pollution"]["aqius"],
                    "main_pollutant": data["data"]["current"]["pollution"]["mainus"]
                }

                # 요청 횟수 증가 (429 오류가 발생해도 증가해야 함)
                api_request_count += 1

                # 캐시에 저장
                air_quality_cache[cache_key] = air_quality
                return air_quality

        except requests.exceptions.RequestException as e:
            if response.status_code == 429:  # Too Many Requests
                print(f"⚠️ API 요청 초과(429) 발생. 10초 후 재시도... (시도 {attempt + 1}/3)")
                time.sleep(10)
            else:
                print(f"❌ API 요청 실패: {e}")
                break

    return None

# 공기질 평가 함수
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

# 산책로 추천 로직
def recommend_walk_courses(user_lat, user_lon):
    courses = fetch_walk_courses()
    recommendations = []

    for course in courses:
        air_quality = fetch_air_quality(course["lat"], course["lon"])
        if air_quality is None:
            print(f"🚫 {course['name']} 산책로에서 공기질 데이터를 가져올 수 없습니다.")
            continue

        aqius = air_quality["aqius"]
        if aqius <= 100:  # AQI 100 이하만 추천
            recommendations.append({
                "name": course["name"],
                "distance": course["distance"],
                "lead_time": course["lead_time"],
                "aqi": aqius,
                "air_quality": evaluate_air_quality(aqius),
                "main_pollutant": air_quality["main_pollutant"]
            })

    return recommendations

# 실행 및 결과 출력
if __name__ == "__main__":
    try:
        # 사용자 위치 (예: 서울 시청)
        user_lat, user_lon = 37.5665, 126.9780

        # 추천 산책로 가져오기
        recommendations = recommend_walk_courses(user_lat, user_lon)

        # 결과 출력
        for rec in recommendations:
            print(f"🌿 산책로: {rec['name']}")
            print(f"📏 거리: {rec['distance']} km, ⏳ 예상 소요 시간: {rec['lead_time']} 분")
            print(f"🌫 AQI: {rec['aqi']}, 🌎 공기질 상태: {rec['air_quality']}")
            print(f"🔬 주요 오염물질: {rec['main_pollutant']}")
            print("-" * 30)

    except Exception as e:
        print(f"🚨 오류 발생: {e}")
