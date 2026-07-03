# Computer Vision & Media Utilities

A collection of lightweight Python tools for video processing, desktop playback, and object tracking.

---

## 🛠️ Included Projects

### 1. Object Tracking Pipeline (`Object Tracking Video/`)
A standalone computer vision script that processes video files to track moving objects and calculate analytics.
* **Core Tech:** OpenCV (`cv2`), NumPy.
* **Features:** Background subtraction (MOG2), contour detection, and Intersection over Union (IoU) tracking. 
* **Output:** Generates a structured CSV file containing frame-by-frame coordinates, travel direction, and estimated velocity tracking.

### 2. Desktop Video Player (`stand_alone_video_player.py`)
A custom desktop media player GUI built to allow precise frame-by-frame inspection and variable playback controls.
* **Core Tech:** Tkinter, Pillow (PIL), OpenCV.
* **Features:** 
  * Adjustable playback speed (from -16.0x reverse up to +16.0x forward).
  * Precise frame stepping using keyboard arrow keys.
  * Direct jumping to specific frame numbers or exact timestamps.
  * Responsive progress bar scrubbing.

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install opencv-python numpy Pillow