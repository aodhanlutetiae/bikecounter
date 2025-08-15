from ultralytics import YOLO
import cv2
from datetime import datetime
import csv

# Input source: 0 for webcam, or a video file path
source = "video_files/cyclists_clip.mp4"  # or 0 for webcam

# COCO class ID for bicycle
BICYCLE_CLASS_ID = 1

# Set of tracked unique bicycle IDs
seen_bike_ids = set()

# make a CSV output file
csv_filename = "bicycle_log.csv"
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["bicycle_id", "timestamp_frame"])  # header row

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Run tracking with ByteTrack
results = model.track(
    source=source,
    tracker="bytetrack.yaml",
    persist=True,
    stream=True,
)

# Process each frame
for result in results:
    # Skip if no tracked objects
    if result.boxes.id is None:
        continue

    ids = result.boxes.id.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy()

    for obj_id, cls_id in zip(ids, classes):
        if int(cls_id) == BICYCLE_CLASS_ID:
            if int(obj_id) not in seen_bike_ids:
                seen_bike_ids.add(int(obj_id))
                
                # Log to CSV only for new cyclist
                with open(csv_filename, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([int(obj_id), datetime.now().isoformat()])

    # Display results
    annotated_frame = result.plot()
    cv2.putText(
        annotated_frame,
        f"Unique bicycles: {len(seen_bike_ids)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )
    cv2.imshow("YOLOv8 + ByteTrack - Bicycle Count", annotated_frame)

    # press q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()

print(f"Total unique bicycles detected: {len(seen_bike_ids)}")
