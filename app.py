from flask import Flask, jsonify, request
import mysql.connector
import requests
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="projwildlife.cxm82ssqs51s.eu-north-1.rds.amazonaws.com",
    user="admin",
    password="admin123",
    database="project"
)
cursor = db.cursor(dictionary=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KE")

def get_coordinates_from_place(place_name):
    """Convert a place name to latitude and longitude using Google Geocoding API."""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={place_name}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()   #print("Google API Response:", data) troubleshoot
    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        return None, None

# Haversine SQL query for nearby detections
HAVERSINE_SQL = """
    SELECT *, 
        (6371 * ACOS(
            COS(RADIANS(%s)) * COS(RADIANS(latitude)) * 
            COS(RADIANS(longitude) - RADIANS(%s)) + 
            SIN(RADIANS(%s)) * SIN(RADIANS(latitude))
        )) AS distance
    FROM detections
    HAVING distance < %s
    ORDER BY detection_time DESC
    LIMIT 10;
"""

@app.route('/latest-spotting', methods=['GET'])
def latest_spotting():
    """Find the latest animal spotting near a given location (lat/lng or place name)."""
    
    place_name = request.args.get('place')  # e.g., "Nairobi National Park"
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', type=int, default=10)  # Default radius: 10 km

    if place_name:
        lat, lng = get_coordinates_from_place(place_name)
        if lat is None or lng is None:
            return jsonify({"error": "Invalid place name"}), 400

    if lat is not None and lng is not None:
        cursor.execute(HAVERSINE_SQL, (lat, lng, lat, radius))
        data = cursor.fetchall()
    else:
        return jsonify({"error": "Please provide a place name or latitude/longitude"}), 400

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
