# Automated Weed Detection & Classification System

An end-to-end computer vision and web application framework designed for automated detection, classification, and management of invasive agricultural weeds using YOLO object detection architectures.

---

## 🌿 Problem Statement & Background

Invasive weed species such as *Amaranthus palmeri* (Palmer amaranth) present severe threats to crop yields due to their rapid growth rate, high reproductive output, and extensive pollen-mediated gene flow (Sarangi et al., 2017; Borgato et al., 2025). 

The rapid proliferation of target-site and non-target-site metabolic herbicide resistance across *Amaranthus* populations makes conventional broad-spectrum chemical application increasingly ineffective (Shyam et al., 2021). This system leverages real-time deep learning detection to enable precision micro-targeting, reducing chemical dependency and mitigating resistance selection pressures.

---

## 📁 Repository Structure

```text
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

## 💡 Acknowledgements & Development Note

The core conceptualization, system architecture, and agricultural domain logic for this project were entirely designed by the author. Generative AI tools were utilized to assist with rapid boilerplate development, API structuring, and frontend-backend integration.