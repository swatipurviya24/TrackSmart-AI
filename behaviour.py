# download_dataset.py
import os
from roboflow import Roboflow

# 1. Install roboflow (if not already installed)
# pip install roboflow

# 2. Set where to save dataset
save_path = "behavior_dataset"

# Create folder if it doesn't exist
os.makedirs(save_path, exist_ok=True)

# 3. Roboflow API
rf = Roboflow(api_key="YOUR_API_KEY")  # <-- Put your Roboflow API key here
project = rf.workspace().project("student-behaviour-detection-neazg-ajd3k")
dataset = project.version(1).download("yolov8", location=save_path)

print(f"✅ Dataset downloaded to {save_path}")
