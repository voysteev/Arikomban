import cv2
import telebot
import mysql.connector
from datetime import datetime
from ultralytics import YOLO

# Telegram Bot Setup
BOT_TOKEN = "7506176766:AAHwb3LCyiqAPAkC02_9bjAQNQkxIOzaND4"
CHAT_ID = "922404220"
bot = telebot.TeleBot(BOT_TOKEN)

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

# Function to store detections in MySQL
def save_detection(animal_name, image_url):
    detection_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    location = "Your Webcam Location"  # Change this if you have GPS coordinates

    query = "INSERT INTO detections (animal_name, detection_time, location, image_url) VALUES (%s, %s, %s, %s)"
    values = (animal_name, detection_time, location, image_url)

    cursor.execute(query, values)
    db.commit()

# Function to send alerts to Telegram
def send_alert(animal, image_path):
    if animal.lower() == "person":
        return  

    message = f"🚨 Alert! {animal} detected!"
    bot.send_message(CHAT_ID, message)
    
    with open(image_path, "rb") as photo:
        bot.send_photo(CHAT_ID, photo)

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

                detected_frame_path = "detected_animal.jpg"
                cv2.imwrite(detected_frame_path, frame)

                send_alert(animal_name, detected_frame_path)
                save_detection(animal_name, "https://your-s3-bucket/detected_animal.jpg")  # Replace with your S3 image URL

    cv2.imshow("Live Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
cursor.close()
db.close()
