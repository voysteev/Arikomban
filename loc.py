import requests

API_KEY = "AIzaSyD3t4rva-Fr3Z2EpmMpuBxjbVlID3Qw5TI"

def get_geolocation():
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={API_KEY}"
    response = requests.post(url, json={})
    location = response.json().get("location", {})
    return f"{location.get('lat')},{location.get('lng')}"

print(f"Webcam Location: {get_geolocation()}")
