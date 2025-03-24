from ultralytics import YOLO

model = YOLO("./best.pt")

result = model(source=0, show=True)

for r in result:
	boxes = result.boxes
	classes = result.names
