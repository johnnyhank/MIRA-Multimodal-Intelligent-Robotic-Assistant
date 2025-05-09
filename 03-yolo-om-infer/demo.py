from ultralytics import YOLO

# Load a pretrained YOLO model
model = YOLO("./models/yolov10n.pt")

# Run inference on an image
results = model("./bus.jpg",save=True)