from ultralytics import YOLO
from picamera2 import Picamera2
import cv2
from datetime import datetime
import csv
import time
import sys
import os
import logging
from logging.handlers import RotatingFileHandler

# ensure we're running from inside the app folder
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)  # Change CWD to the directory where your script resides

# --- LOGGING SETUP ---
LOG_DIR = '/home/pi/logs'
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, 'pi_run.log')
handler = RotatingFileHandler(LOG_PATH, maxBytes=1024*1024, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s [%(module)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger = logging.getLogger('cyclist_detection')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def log_and_print(level, msg):
    print(msg)
    if level == 'info':
        logger.info(msg)
    elif level == 'debug':
        logger.debug(msg)
    elif level == 'warning':
        logger.warning(msg)
    elif level == 'error':
        logger.error(msg)
    elif level == 'critical':
        logger.critical(msg)

try:
    log_and_print('info', 'Pi powered up, script initialising.')

    # Check virtual environment
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        log_and_print('info', f'Virtual environment activated: {venv}')
        if not venv.endswith('bike_env'):
            log_and_print('warning', 'bike_env is not active.')
    else:
        log_and_print('warning', 'Virtual environment NOT activated.')

    # Wait for 3 minutes for box installation
    log_and_print('info', 'Waiting 3 minutes for installation of box...')
    time.sleep(180)

    # Set up duration of runtime and the start time
    MAX_RUNTIME = 3600
    start_time = time.time()

    BICYCLE_CLASS_ID = 1
    seen_bike_ids = set()

    # create or check csv file
    csv_filename = "/media/pi/2D61-74F0/bicycle_log.csv"
    try:
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["bicycle_id", "timestamp_frame"])
        log_and_print('info', f'CSV log file created at {csv_filename}')
    except Exception as e:
        log_and_print('error', f'Failed to create CSV file: {e}')

    # Initialize Picamera2
    try:
        picam2 = Picamera2()
        picam2.start()
        log_and_print('info', "Picamera2 initialised and started.")
    except Exception as e:
        log_and_print('error', f'Failed to initialise Picamera2: {e}')
        raise

    # Take and save a still image
    image_filename = "/media/pi/2D61-74F0/startup_photo.jpg"
    try:
        picam2.capture_file(image_filename)
        log_and_print('info', f"Startup photo captured at {image_filename}")
    except Exception as e:
        log_and_print('error', f'Failed to capture startup photo: {e}')

    # Load YOLOv8 model
    try:
        model = YOLO("yolov8n.pt")
        log_and_print('info', "YOLOv8 model loaded.")
    except Exception as e:
        log_and_print('error', f'Failed to load YOLOv8 model: {e}')
        raise

    log_and_print('info', 'Cyclist detection loop starting...')

    while True:
        try:
            frame = picam2.capture_array()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            results = model.track(
                frame_rgb,
                tracker="bytetrack.yaml",
                persist=True
            )

            for result in results:
                if result.boxes.id is None:
                    continue
                ids = result.boxes.id.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy()
                for obj_id, cls_id in zip(ids, classes):
                    if int(cls_id) == BICYCLE_CLASS_ID:
                        if int(obj_id) not in seen_bike_ids:
                            seen_bike_ids.add(int(obj_id))
                            try:
                                with open(csv_filename, mode='a', newline='') as file:
                                    writer = csv.writer(file)
                                    writer.writerow([int(obj_id), datetime.now().isoformat()])
                                log_and_print('info', f'Logged bicycle ID {int(obj_id)} at {datetime.now().isoformat()}')
                            except Exception as e:
                                log_and_print('error', f'Failed to log bicycle ID {int(obj_id)}: {e}')

        except Exception as e:
            log_and_print('error', f'Error during frame processing: {e}')

        # check if the time limit has been reached
        if time.time() - start_time > MAX_RUNTIME:
            log_and_print('info', f'Maximum runtime ({MAX_RUNTIME}s) reached, exiting.')
            break

    log_and_print('info', f'Cyclist detection loop finished. Number of unique cyclists detected: {len(seen_bike_ids)}')

except Exception as e:
    logger.exception('Unhandled exception occurred:')
finally:
    log_and_print('info', 'Script exited cleanly.')

logger.info("")  # Logs a blank line

# os.system("sudo shutdown -h now")
# sys.exit(0)
