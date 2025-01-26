import requests

API_KEY = "7aa890fa-64df-4bea-9a25-9647060415d8"
LAT, LON = 37.5665, 126.9780
response = requests.get(
    f"http://api.airvisual.com/v2/nearest_city?lat={LAT}&lon={LON}&key={API_KEY}"
)
print(response.json())