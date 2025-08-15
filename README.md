**Cyclist counter**

This application will run on a Raspberry Pi and if you set your camera on a street or bikepath will keep a count of cyclists. It needs

- Raspberry Pi (4B recommended)
- Python 3.10.13 (best installed using pyenv)
- Camera
- Battery pack
- USB drive

## TRACKER

Once you've installed a Python virtual environment, the bytetracks file that sets the parameters on the tracker can be found (on a mac) at: 

<your_virtual_env>/lib/python3.10/site-packages/ultralytics/cfg/trackers/bytetrack.yaml

We adjusted "track_high_thresh" to 0.5 and "new_track_thresh" to 0.6 which left the following parameters:

tracker_type: bytetrack 
track_high_thresh: 0.5 
track_low_thresh: 0.1 
new_track_thresh: 0.6 
track_buffer: 30  
match_thresh: 0.8  
fuse_score: True  

---

## USB

Saving to the Pi's external USB will require

csv_filename = "bicycle_log.csv"
usb_path = '/Volumes/data'
os.makedirs(usb_path, exist_ok=True)
csv_file_path = os.path.join(usb_path, csv_filename)
