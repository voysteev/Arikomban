import cv2
import telebot
from ultralytics import YOLO

BOT_TOKEN = ""
CHAT_ID = ""
bot = telebot.TeleBot(BOT_TOKEN)
previous = "person"

model = YOLO("/home/user/voy/best.pt")  


cap = cv2.VideoCapture(0)  


'''def send_alert(animal, image_path):
    if animal.lower() == "person":
        return
    elif previous == animal.lower():
	return
    previous = animal.lower()	
    message = f"🚨 Alert! {animal} detected!"
    bot.send_message(CHAT_ID, message)    
    with open(image_path, "rb") as photo:
        bot.send_photo(CHAT_ID, photo)'''

def send_alert(animal, image_path):
    global previous   # Ensure 'previous' is recognized as a global variable
    if animal.lower() == "person":
        return
    elif previous == animal.lower():
        return
    previous = animal.lower()   
    message = f"🚨 Alert! {animal} detected!"
    bot.send_message(CHAT_ID, message)    
    with open(image_path, "rb") as photo:
        bot.send_photo(CHAT_ID, photo)
  


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

    
    cv2.imshow("Live Feed", frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

