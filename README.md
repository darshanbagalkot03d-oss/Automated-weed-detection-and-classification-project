# Automated Weed Detection & Classification System

An end-to-end computer vision and web application framework designed for automated detection, classification, and management of invasive agricultural weeds using YOLO object detection architectures.

---

## 🌿 Problem Statement & Background

Invasive weed species such as *Amaranthus palmeri* (Palmer amaranth) present severe threats to crop yields due to their rapid growth rate, high reproductive output, and extensive pollen-mediated gene flow (Sarangi et al., 2017; Borgato et al., 2025). 

The rapid proliferation of target-site and non-target-site metabolic herbicide resistance across *Amaranthus* populations makes conventional broad-spectrum chemical application increasingly ineffective (Shyam et al., 2021). This system leverages real-time deep learning detection to enable precision micro-targeting, reducing chemical dependency and mitigating resistance selection pressures.

---
## 📁 Repository Structure

```text
├── assets/                   # Evaluation graphs, metric curves, and UI screenshots
│   ├── Grph1.jpg             # Precision, Recall, mAP50, mAP50-95 curves
│   ├── Grph2.png             # F1 Score over epochs curve
│   ├── Grph3.png             # YOLOv11 Medium training curve
│   ├── Grph4.png             # YOLOv11 Large training curve
│   └── Webpage.jpg           # Dashboard UI interface screenshot
├── backend/                  # API server & model inference endpoints
│   ├── models/               # YOLO inference wrappers
│   ├── best.pt               # Trained YOLO object detection weights
│   └── main.py               # Application entry point
├── frontend/                 # Web interface source code
│   ├── index.html            # Main dashboard UI
│   ├── app.js                # Frontend API client script
│   └── style.css             # Interface styling
├── data_scripts/             # Dataset preprocessing & augmentation tools
│   ├── Data_augumwentation.py # Custom image transformation scripts
│   ├── Predict.py            # Offline image prediction pipeline
│   └── Roboflow.py           # Dataset export/formatting utilities
├── docs/                     # Literature review & research reference papers
└── weights/                  # Archived model checkpoints (.pt)

---

🚀 Key Performance Highlights
Detection & Classification: Real-time computer vision pipeline powered by YOLOv8, trained on a custom-curated dataset of 7,518 images across 5 weed classes.

Accuracy Metrics (COCO Standard): Achieved 70.04% Precision, 63.81% Recall, and a 44.47% mAP@50-95.

Inference Speed: Benchmarked at 30.6 FPS (32.6ms latency) on an NVIDIA T4 GPU at 768px resolution.

Deployment Optimization: Model exported to ONNX format for framework-agnostic portability.

Edge System Architecture: Bypassed mobile hardware processing limitations by routing frame captures to a central GPU-accelerated backend via ngrok, maintaining high accuracy without sacrificing real-time speed.

💻 Web Dashboard & Real-Time Deployment
The project features a full-stack dashboard built with FastAPI/Flask, HTML/CSS/JS, and YOLOv8, allowing farmers and researchers to perform edge detection in real time.

Key Dashboard Capabilities
Dual Inference Pipeline: Real-time webcam video feeds (Live Feed) and static image analysis (Image Upload).

Geospatial Mapping: Integrated GIS mapping (Leaflet/Google Maps) to geotag weed distributions across fields.

Target Species Logging: Real-time log tracking for identified species (Amaranthus palmeri, Echinochloa colona, Ryegrass).

Edge System Architecture: Bypassed mobile hardware processing limitations by routing frame captures to a central GPU-accelerated backend via ngrok.

📓 Detailed Logs & Documentation
For a complete breakdown of dataset rebalancing, custom Python augmentations, hyperparameter tuning (Mosaic, Mixup), and step-by-step training iterations, refer to the [TRAINING_LOG.md](TRAINING_LOG.md).

---

⚙️ Quick Start / How to Run

# Clone the repository
git clone [https://github.com/your-username/weed-detection-project.git](https://github.com/your-username/weed-detection-project.git)
cd weed-detection-project

# Install backend dependencies
pip install ultralytics fastapi uvicorn opencv-python

# Run the backend API server
python backend/main.py

💡 Acknowledgements & Development Note
The core conceptualization, system architecture, agricultural domain logic, and iterative model evaluation for this project were designed and executed by the author. Generative AI tools were utilized to assist with rapid script syntax, API structuring, and frontend-backend integration.