import os
import uuid
import io
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from PIL import Image
from models.yolo_model import YOLO_Model 
from db import init_db, SessionLocal, Detection
from weed_info import WEED_INFO
from datetime import timedelta


base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.normpath(os.path.join(base_dir, '..', 'frontend'))

app = Flask(__name__, 
            template_folder=frontend_dir, 
            static_folder=frontend_dir,
            static_url_path='')
CORS(app) 


MEDIA_FOLDER = os.path.join(base_dir, 'processed_media')
if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER, exist_ok=True)

MODEL_PATH = os.path.join(base_dir, 'best.pt') 

model = None
try:
    if os.path.exists(MODEL_PATH):
        model = YOLO_Model(MODEL_PATH)
        print(f"✅ YOLO model loaded successfully from {MODEL_PATH}")
    else:
        print(f"❌ CRITICAL: model file not found at {MODEL_PATH}")
except Exception as e:
    print(f"❌ MODEL INITIALIZATION ERROR: {e}")

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_media():
    if not model:
        return jsonify({'status': 'error', 'message': 'AI Model not initialized on server'}), 500
    
    file = request.files.get('file')
    if not file:
        return jsonify({'status': 'error', 'message': 'No image received'}), 400

    try:
        image_data = file.read()
        
        # 3. AI Prediction 
        # Ensure your yolo_model.py returns (results_dict, pil_image_object)
        results, annotated_pil_image = model.predict(image_data)
        
        # 4. Save Processed Image
        filename = f"{uuid.uuid4()}.jpg"
        save_path = os.path.join(MEDIA_FOLDER, filename)
        
        # Robust Save: Check if annotated_pil_image is valid
        if annotated_pil_image:
            annotated_pil_image.save(save_path, format='JPEG')
        else:
            # Fallback: if model failed to annotate, save the original
            img = Image.open(io.BytesIO(image_data))
            img.save(save_path, format='JPEG')
            print("⚠️ Warning: Saved raw image because AI annotation failed.")

        # 5. Database Storage
        db = SessionLocal()
        try:
            lat = request.form.get('lat')
            lng = request.form.get('lng')
            def safe_float(val):
                try:
                    return float(val) if val is not None else None
                except (ValueError, TypeError):
                    return None

            detections_list = results.get('detections', [])
            weed_names = list(set(d['name'] for d in detections_list))
            
            new_det = Detection(
                media_path=filename,
                raw_results=results,
                main_weeds=', '.join(weed_names) if weed_names else "No Weeds",
                total_detections=len(detections_list),
                latitude=float(lat) if lat and lat != 'undefined' else None,
                longitude=float(lng) if lng and lng != 'undefined' else None
            )
            db.add(new_det)
            db.commit()
            print(f"✨ Processed: {len(detections_list)} weeds found. Image: {filename}")
        except Exception as db_e:
            print(f"Database Error: {db_e}")
        finally:
            db.close()

        return jsonify({
            'status': 'success',
            'processed_url': f'/api/media/{filename}', 
            'detections': detections_list,
            'analytics': results.get('analytics', {})
        })

    except Exception as e:
        print(f"🔥 Processing Crash: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/media/<filename>')
def get_media(filename):
    file_path = os.path.join(MEDIA_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/jpeg')
    return "Image not found", 404

@app.route('/api/weeds')
def get_weeds_info():
    weeds_list = list(WEED_INFO.values())
    print(f"📡 Sending info for {len(weeds_list)} weeds to frontend")
    return jsonify({'weeds': weeds_list})
    return jsonify({'weeds': list(WEED_INFO.values())})

@app.route('/api/detections/recent')
def get_recent():
    db = SessionLocal()
    try:
        # Fetching the 5 latest entries
        recent = db.query(Detection).order_by(Detection.timestamp.desc()).limit(4).all()
        history = []
        for d in recent:
            # Adjust UTC time to IST (UTC + 5:30)
            ist_time = d.timestamp + timedelta(hours=0, minutes=0)
            
            history.append({
                'main_weeds': d.main_weeds if d.main_weeds else "No weeds detected", 
                'total_detections': d.total_detections,
                'timestamp': ist_time.strftime("%b %d, %I:%M %p"),# Use %I:%M %p for 12-hour AM/PM format
                'lat': d.latitude,
                'lng': d.longitude
            })
        return jsonify({'history': history})
    except Exception as e:
        print(f"❌ History Fetch Error: {e}")
        return jsonify({'history': [], 'error': str(e)})
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)