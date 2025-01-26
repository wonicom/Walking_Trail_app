import requests

SEOUL_API_KEY = "57665a72576330393834646b496a75"
response = requests.get(
    f"http://openAPI.seoul.go.kr:8088/{SEOUL_API_KEY}/xml/SeoulGilWalkCourse/1/5"
)
print(response.content)
