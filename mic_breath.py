import sounddevice as sd
import numpy as np
import librosa
from scipy.signal import find_peaks


def detect_breath_from_mic(duration=12, fs=22050):

    print("Recording breathing audio...")
    try:
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
    except Exception as e:
        print(f"Microphone error: {e}")
        return 0, "Microphone Error", []
    
    audio = audio.flatten()

    # Remove silence - less aggressive trimming for quiet breathing
    audio = librosa.effects.trim(audio, top_db=15)[0]

    if len(audio) < fs:
        return 0, "No breathing detected", []

    # Bandpass filter (breathing range ~100–1000 Hz)
    audio = librosa.effects.preemphasis(audio)

    # Compute energy envelope
    rms = librosa.feature.rms(y=audio)[0]

    # Smooth envelope
    rms = np.convolve(rms, np.ones(10)/10, mode='same')

    # Normalize
    rms = (rms - np.mean(rms)) / (np.std(rms) + 1e-6)

    # Detect peaks (breath cycles)
    peaks, _ = find_peaks(
        rms,
        distance=25,       # Allow ~70 bpm max
        prominence=0.15    # Much more sensitive threshold
    )

    breaths = len(peaks)
    breaths_per_min = round((breaths / duration) * 60, 2)

    if breaths_per_min == 0:
        # even if 0, return the signal so we see the flatline
        return 0, "No breathing detected", rms.tolist()

    if breaths_per_min < 10:
        status = "Slow / Calm"
    elif breaths_per_min < 20:
        status = "Normal"
    else:
        status = "Fast / Stressed"

    return breaths_per_min, status, rms.tolist()


if __name__ == "__main__":

    rate, status = detect_breath_from_mic()

    print("Breaths per minute:", rate)
    print("Status:", status)
