import requests
import xml.etree.ElementTree as ET
from pyproj import Proj, Transformer
import time
from cachetools import TTLCache

# 🔹 API Keys
SEOUL_API_KEY = "57665a72576330393834646b496a75"
IQAIR_API_KEY = "7aa890fa-64df-4bea-9a25-9647060415d8"

# 🔹 API Limits & Caching
API_REQUEST_LIMIT = 10
api_request_count = 0
air_quality_cache = TTLCache(maxsize=100, ttl=300)  # Cache for 5 minutes


# 🔹 Coordinate Transformation (GRS80TM → WGS84)
def convert_grs80_to_wgs84(x, y):
    transformer = Transformer.from_proj(
        Proj(proj='tmerc', lat_0=38, lon_0=127.5, k=1.0, x_0=200000, y_0=500000, ellps='GRS80', units='m'),
        Proj(proj='latlong', datum='WGS84'),
        always_xy=True
    )
    lon, lat = transformer.transform(x, y)
    return lat, lon


# 🔹 Fetch Walking Trails from Seoul API
def fetch_walk_courses(start_index=1, end_index=20):
    url = f"http://openAPI.seoul.go.kr:8088/{SEOUL_API_KEY}/xml/SeoulGilWalkCourse/{start_index}/{end_index}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        walk_courses = []
        seen_courses = set()  # Prevent duplicate trails

        for row in root.findall(".//row"):
            name = row.find("COURSE_NAME").text
            if name in seen_courses:
                continue

            x = float(row.find("X").text)
            y = float(row.find("Y").text)

            lat, lon = convert_grs80_to_wgs84(x, y)
            walk_courses.append({"name": name, "lat": lat, "lon": lon})
            seen_courses.add(name)

        return walk_courses

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch walk courses: {e}")
        return []


# 🔹 Fetch Air Quality Data from IQAir API
def fetch_air_quality(lat, lon):
    global api_request_count

    # Check API request limit
    if api_request_count >= API_REQUEST_LIMIT:
        return None

    # Use cached data if available
    cache_key = (round(lat, 3), round(lon, 3))
    if cache_key in air_quality_cache:
        return air_quality_cache[cache_key]

    url = f"http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={IQAIR_API_KEY}"

    try:
        time.sleep(1)  # Prevent rapid requests
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "success":
            air_quality = data["data"]["current"]["pollution"]["aqius"]

            # Increment API request count
            api_request_count += 1

            # Store in cache
            air_quality_cache[cache_key] = air_quality
            return air_quality

    except requests.exceptions.RequestException:
        return None

    return None


# 🔹 Evaluate Air Quality Level
def evaluate_air_quality(aqi):
    if aqi is None:
        return "No Data ❌"
    elif aqi <= 50:
        return "Good 🟢"
    elif aqi <= 100:
        return "Moderate 🟡"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups 🟠"
    elif aqi <= 200:
        return "Unhealthy 🔴"
    elif aqi <= 300:
        return "Very Unhealthy 🟣"
    else:
        return "Hazardous ⚫"


# 🔹 Calculate the Average AQI
def calculate_average_aqi():
    trails = fetch_walk_courses(1, 20)  # Fetch the first 20 trails
    total_aqi = 0
    count = 0

    for trail in trails:
        air_quality = fetch_air_quality(trail["lat"], trail["lon"])
        if air_quality is None:
            continue  # Skip if no AQI data available

        total_aqi += air_quality
        count += 1

    # 평균 AQI 계산 (유효한 데이터만 포함)
    average_aqi = round(total_aqi / count, 2) if count > 0 else None
    return average_aqi


# 🔹 Run & Display Results
if __name__ == "__main__":
    try:
        average_aqi = calculate_average_aqi()

        if average_aqi is not None:
            print(f"\n📊 Average AQI for Recommended Walking Trails: {average_aqi} ({evaluate_air_quality(average_aqi)})")
        else:
            print("\n⚠️ No valid AQI data available for recommended trails.")

    except Exception as e:
        print(f"🚨 Error occurred: {e}")
