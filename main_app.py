from breath_detector import run_breath_detection
from mic_breath import detect_breath_from_mic
from voice_stress import record_audio, analyze_voice


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

    # Weighted fusion
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


if __name__ == "__main__":

    print("\n===== AI MULTIMODAL STRESS SYSTEM =====\n")

    # 1️⃣ Camera Breathing
    cam_rate, _ = run_breath_detection()
    print("Camera Breathing Rate:", cam_rate)

    # 2️⃣ Mic Breathing
    mic_rate, _ = detect_breath_from_mic()
    print("Mic Breathing Rate:", mic_rate)

    # 3️⃣ Voice Stress
    audio, fs = record_audio()
    voice_score, _ = analyze_voice(audio, fs)
    print("Voice Stress Score:", voice_score)

    # Final Fusion
    final_score, level = combine_scores(
        cam_rate,
        mic_rate,
        voice_score
    )

    print("\n===============================")
    print("FINAL STRESS SCORE:", final_score)
    print("FINAL STRESS LEVEL:", level)
    print("===============================\n")
