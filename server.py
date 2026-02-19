import logging
import sys

# Setup logging immediately
logging.basicConfig(filename='server_debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Server script started")

try:
    from flask import Flask, jsonify
except ImportError as e:
    logging.critical(f"Failed to import Flask: {e}")
    sys.exit(1)

# from flask import Flask, jsonify
# from flask_cors import CORS
# from flask import send_file


# from breath_detector import run_breath_detection
# from mic_breath import detect_breath_from_mic
# from voice_stress import record_audio, analyze_voice

# app = Flask(__name__)
# CORS(app)


# def breathing_score(rate):

#     if rate == 0:
#         return 0

#     if rate < 8:
#         return 20
#     elif rate < 14:
#         return 40
#     elif rate < 20:
#         return 60
#     else:
#         return 85


# def combine_scores(cam_rate, mic_rate, voice_score):

#     cam_score = breathing_score(cam_rate)
#     mic_score = breathing_score(mic_rate)

#     final_score = (
#         0.3 * cam_score +
#         0.3 * mic_score +
#         0.4 * voice_score
#     )

#     final_score = round(final_score, 2)

#     if final_score < 40:
#         level = "Low Stress"
#     elif final_score < 70:
#         level = "Moderate Stress"
#     else:
#         level = "High Stress"

#     return final_score, level


# @app.route("/")
# def home():
#     return jsonify({"message": "AI Stress Detection API Running"})

# @app.route("/ui")
# def ui():
#     return send_file("index.html")



# @app.route("/analyze", methods=["GET"])
# def analyze():

#     # 1️⃣ Camera breathing
#     cam_rate, _ = run_breath_detection()

#     # 2️⃣ Mic breathing
#     mic_rate, _ = detect_breath_from_mic()

#     # 3️⃣ Voice stress
#     audio, fs = record_audio()
#     voice_score, _ = analyze_voice(audio, fs)

#     final_score, level = combine_scores(
#         cam_rate,
#         mic_rate,
#         voice_score
#     )

#     return jsonify({
#         "camera_breath_rate": cam_rate,
#         "mic_breath_rate": mic_rate,
#         "voice_score": voice_score,
#         "final_stress_score": final_score,
#         "stress_level": level
#     })


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

from breath_detector import run_breath_detection
from mic_breath import detect_breath_from_mic
from voice_stress import record_audio, analyze_voice

app = Flask(__name__)
CORS(app)


def breathing_score(rate):

    if rate == 0:
        return 0

    if rate < 8:
        return 20
    elif rate < 14:
        return 40
    elif rate < 20:
        return 60
    else:
        return 85


def combine_scores(cam_rate, mic_rate, voice_score):

    cam_score = breathing_score(cam_rate)
    mic_score = breathing_score(mic_rate)

    final_score = (
        0.3 * cam_score +
        0.3 * mic_score +
        0.4 * voice_score
    )

    final_score = round(final_score, 2)

    if final_score < 40:
        level = "Low Stress"
    elif final_score < 70:
        level = "Moderate Stress"
    else:
        level = "High Stress"

    return final_score, level


@app.route("/")
def home():
    return jsonify({"message": "AI Stress Backend Running"})


 



def get_suggestions(score, cam_rate, mic_rate, voice_score):
    suggestions = []
    
    # Breathing specific
    if cam_rate > 20 or mic_rate > 20:
        suggestions.append("Your breathing is fast. Try the 4-7-8 technique: Inhale for 4s, hold for 7s, exhale for 8s.")
    elif cam_rate < 6 and cam_rate > 0:
        suggestions.append("Your breathing is very slow. Take steady, natural breaths.")
        
    # Voice specific
    if voice_score > 50:
        suggestions.append("Your voice shows signs of tension. Try to speak slower and lower your pitch slightly.")
    
    # General Stress
    if score < 40:
        suggestions.append("You are in a good state! Keep up your routine.")
    elif score < 70:
        suggestions.append("Moderate stress detected. Take a short walk or drink some water.")
    else:
        suggestions.append("High stress level. We recommend a 5-minute break and deep breathing exercises immediately.")
        
    return suggestions

@app.route("/cam")
def cam_step():
    try:
        cam_rate, status, signal = run_breath_detection()
        # verify signal is list
        if not isinstance(signal, list): signal = []
        
        if cam_rate == 0 and status != "Normal":  # minimal check
             return jsonify({"ok": False, "error": status, "camera_breath_rate": 0, "signal": signal})
             
        return jsonify({"ok": True, "camera_breath_rate": float(cam_rate), "signal": signal})
    except Exception as e:
        logging.error(f"Cam Error: {e}")
        return jsonify({"ok": False, "error": str(e), "camera_breath_rate": 0, "signal": []})


@app.route("/mic")
def mic_step():
    try:
        mic_rate, status, signal = detect_breath_from_mic()
        if not isinstance(signal, list): signal = []
        
        if mic_rate == 0 and status != "Normal":
            return jsonify({"ok": False, "error": status, "mic_breath_rate": 0, "signal": signal})
        return jsonify({"ok": True, "mic_breath_rate": float(mic_rate), "signal": signal})
    except Exception as e:
        logging.error(f"Mic Error: {e}")
        return jsonify({"ok": False, "error": str(e), "mic_breath_rate": 0, "signal": []})


@app.route("/voice")
def voice_step():
    try:
        audio, fs = record_audio()
        voice_score, level, signal = analyze_voice(audio, fs)
        if not isinstance(signal, list): signal = []
        
        if voice_score == 0:
            return jsonify({"ok": False, "error": level, "voice_score": 0, "signal": signal})
        return jsonify({"ok": True, "voice_score": float(voice_score), "level": level, "signal": signal})
    except Exception as e:
        logging.error(f"Voice Error: {e}")
        return jsonify({"ok": False, "error": str(e), "voice_score": 0, "signal": []})


@app.route("/analyze")
def analyze():
    try:
        cam_rate, cam_status, _ = run_breath_detection()
    except: cam_rate, cam_status = 0, "Error"
    
    try:
        mic_rate, mic_status, _ = detect_breath_from_mic()
    except: mic_rate, mic_status = 0, "Error"
    
    try:
        audio, fs = record_audio()
        voice_score, voice_status, _ = analyze_voice(audio, fs)
    except: voice_score, voice_status = 0, "Error"
    
    final_score, level = combine_scores(cam_rate, mic_rate, voice_score)
    
    tips = get_suggestions(final_score, cam_rate, mic_rate, voice_score)
    
    return jsonify({
        "camera_breath_rate": float(cam_rate),
        "camera_status": cam_status,
        "mic_breath_rate": float(mic_rate),
        "mic_status": mic_status,
        "voice_score": float(voice_score),
        "voice_status": voice_status,
        "final_stress_score": float(final_score),
        "stress_level": level,
        "suggestions": tips
    })


if __name__ == "__main__":
    # Disable debug to prevent reloader issues and bind to all interfaces
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
