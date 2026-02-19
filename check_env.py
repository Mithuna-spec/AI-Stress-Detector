import sys
print("Starting import check...", flush=True)
try:
    import flask
    print("Flask OK", flush=True)
    import cv2
    print("OpenCV OK", flush=True)
    import numpy
    print("Numpy OK", flush=True)
    import scipy
    print("Scipy OK", flush=True)
    import sounddevice
    print("Sounddevice OK", flush=True)
    import librosa
    print("Librosa OK", flush=True)
    print("ALL IMPORTS OK", flush=True)
except Exception as e:
    print(f"IMPORT ERROR: {e}", flush=True)
