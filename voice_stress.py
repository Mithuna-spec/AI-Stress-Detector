import sounddevice as sd
import numpy as np
import librosa
import time


def record_audio(duration=4, fs=22050):

    print("Recording voice for", duration, "seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    print("Recording complete.")
    return audio.flatten(), fs


def analyze_voice(audio, fs):

    # Trim silence
    audio = librosa.effects.trim(audio, top_db=20)[0]

    if len(audio) < fs:
        return 0, "Voice too short", []

    # -----------------------
    # 1️⃣ Energy Features
    # -----------------------
    rms = librosa.feature.rms(y=audio)[0]
    energy_mean = np.mean(rms)
    energy_std = np.std(rms)

    # -----------------------
    # 2️⃣ Speech Rate Proxy
    # -----------------------
    zcr = librosa.feature.zero_crossing_rate(audio)[0]
    zcr_mean = np.mean(zcr)

    print("Energy Mean:", round(energy_mean, 4))
    print("Energy STD:", round(energy_std, 4))
    print("ZCR Mean:", round(zcr_mean, 4))

    stress_score = 0

    # Loudness contribution (0-40)
    loudness_score = min(energy_mean * 400, 40)  # Scaling factor adjusted

    # Variability contribution (0-30)
    variability_score = min(energy_std * 300, 30)

    # Speed/ZCR contribution (0-30)
    zcr_score = min(zcr_mean * 500, 30)

    stress_score = loudness_score + variability_score + zcr_score
    stress_score = round(stress_score, 2)

    stress_score = round(stress_score, 2)

    if stress_score < 40:
        level = "Calm Voice"
    elif stress_score < 70:
        level = "Moderate Stress"
    else:
        level = "High Vocal Stress"

    return stress_score, level, rms.tolist()



if __name__ == "__main__":

    audio, fs = record_audio()
    score, level = analyze_voice(audio, fs)

    print("\nVoice Stress Score:", score)
    print("Voice Stress Level:", level)
