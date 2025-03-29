import cv2
import telebot
import mysql.connector
import boto3
from datetime import datetime
from ultralytics import YOLO

# Telegram Bot Setup
BOT_TOKEN = ""
CHAT_ID = ""
bot = telebot.TeleBot(BOT_TOKEN)

# AWS S3 Configuration
S3_BUCKET = "wildlifedetections"
S3_REGION = "eu-north-1"
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""

# Initialize S3 Client
s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

# MySQL Database Connection (AWS RDS)
db = mysql.connector.connect(
    host="projwildlife.cxm82ssqs51s.eu-north-1.rds.amazonaws.com",
    user="admin",
    password="admin123",
    database="project"
)
cursor = db.cursor()

# Load YOLO model
model = YOLO("/home/user/voy/best.pt")

# Open webcam
cap = cv2.VideoCapture(0)

# Initialize `previous` as a global variable at the top
previous = None  # ✅ Fix: Define it at the beginning

# Function to upload image to S3
def upload_to_s3(file_path, file_name):
    try:
        s3.upload_file(file_path, S3_BUCKET, file_name)
        s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_name}"
        return s3_url
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None

# Function to store detections in MySQL
def save_detection(animal_name, image_url):
    detection_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    location = "Your Webcam Location"  

    query = "INSERT INTO detections (animal_name, detection_time, location, image_url) VALUES (%s, %s, %s, %s)"
    values = (animal_name, detection_time, location, image_url)

    cursor.execute(query, values)
    db.commit()

# Function to send alerts to Telegram
def send_alert(animal, image_url):
    message = f"🚨 Alert! {animal} detected!"
    bot.send_message(CHAT_ID, message)
    bot.send_photo(CHAT_ID, image_url)

# Main loop for YOLO detection
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  

    results = model(frame)

    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])   
            conf = float(box.conf[0])

            if conf > 0.5:  
                animal_name = model.names[cls_id]
                print(f"{animal_name} detected!")

                x1, y1, x2, y2 = map(int, box.xyxy[0])  
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)  
                cv2.putText(frame, animal_name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Fix: Use `global previous` before modifying it
                global previous  

                # Prevent duplicate alerts
                if animal_name.lower() == "person":
                    continue
                elif previous == animal_name.lower():
                    continue

                # Fix: Assign correctly instead of using `==`
                previous = animal_name.lower()

                # Save the detected image
                detected_frame_path = "detected_animal.jpg"
                cv2.imwrite(detected_frame_path, frame)

                # Upload to S3 and get URL
                s3_image_url = upload_to_s3(
                    detected_frame_path,
                    f"{animal_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                )

                if s3_image_url:
                    send_alert(animal_name, s3_image_url)
                    save_detection(animal_name, s3_image_url)

    cv2.imshow("Live Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
cursor.close()
db.close()
