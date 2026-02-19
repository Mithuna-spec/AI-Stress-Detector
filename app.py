import streamlit as st
import requests
import time

BACKEND_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="AI Stress Detector", layout="wide")

st.title("AI Multimodal Stress Detection System")

st.markdown("Real-time stress detection using Camera + Microphone + Voice")

st.markdown("---")


# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------
def breathing_score(rate: float) -> int:
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


def combine_scores(cam_rate: float, mic_rate: float, voice_score: float):
    cam_score = breathing_score(cam_rate)
    mic_score = breathing_score(mic_rate)
    final = round(0.3 * cam_score + 0.3 * mic_score + 0.4 * voice_score, 2)
    if final < 40:
        level = "Low Stress"
    elif final < 70:
        level = "Moderate Stress"
    else:
        level = "High Stress"
    return final, level


# ---------------------------------------------------------------------
# SHARED FUNCTION TO RUN ANALYSIS SEQUENTIALLY
# ---------------------------------------------------------------------
def run_full_analysis():
    results = {}
    
    # Create a placeholder for status updates
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    try:
        # STEP 1: CAMERA
        status_text.info("📸 Step 1/3: Analyzing Breathing via Camera (15s)... Please sit still.")
        resp = requests.get(f"{BACKEND_URL}/cam", timeout=30)
        data = resp.json()
        if not data.get("ok"):
            st.error(f"Camera failed: {data.get('error')}")
            results["cam_rate"] = 0
            results["cam_signal"] = []
        else:
            results["cam_rate"] = data["camera_breath_rate"]
            results["cam_signal"] = data.get("signal", [])
        progress_bar.progress(33)

        # STEP 2: MIC
        status_text.info("🎙️ Step 2/3: Analyzing Breathing via Mic (12s)... Please remain quiet.")
        resp = requests.get(f"{BACKEND_URL}/mic", timeout=30)
        data = resp.json()
        if not data.get("ok"):
            st.error(f"Microphone failed: {data.get('error')}")
            results["mic_rate"] = 0
            results["mic_signal"] = []
        else:
            results["mic_rate"] = data["mic_breath_rate"]
            results["mic_signal"] = data.get("signal", [])
        progress_bar.progress(66)

        # STEP 3: VOICE
        status_text.info("🗣️ Step 3/3: Analyzing Voice Stress (4s)... Read a sentence aloud.")
        resp = requests.get(f"{BACKEND_URL}/voice", timeout=30)
        data = resp.json()
        if not data.get("ok"):
            st.error(f"Voice analysis failed: {data.get('error')}")
            results["voice_score"] = 0
            results["voice_signal"] = []
        else:
            results["voice_score"] = data["voice_score"]
            results["voice_signal"] = data.get("signal", [])
        progress_bar.progress(100)
        
        status_text.success("Analysis Complete!")
        time.sleep(1)
        status_text.empty()
        
        return results

    except requests.exceptions.ConnectionError:
        status_text.empty()
        st.error("❌ CRITICAL ERROR: Could not connect to the backend.")
        st.info("Is the server running? Check 'run_server.bat'.")
        return None
    except Exception as e:
        status_text.empty()
        st.error(f"❌ Error during analysis: {e}")
        return None


if st.button("Run Stress Analysis", key="run_main"):
    data = run_full_analysis()
    
    if data:
        # DISPLAY RESULTS
        st.subheader("Analysis Results")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Camera Breath Rate", data["cam_rate"])
        c2.metric("Mic Breath Rate", data["mic_rate"])
        c3.metric("Voice Stress Score", data["voice_score"])
        
        # Show signals
        if data["cam_signal"]:
            st.caption("Camera Signal")
            st.line_chart(data["cam_signal"], height=100)
        
        if data["mic_signal"]:
            st.caption("Microphone Signal")
            st.line_chart(data["mic_signal"], height=100)
            
        # Calculate Final
        final, level = combine_scores(data["cam_rate"], data["mic_rate"], data["voice_score"])
        
        st.markdown("---")
        st.subheader("Final Stress Report")
        st.metric("Total Stress Score", final)
        st.write(f"**Status:** {level}")
        
        if final < 40:
            st.success("✅ Low Stress")
        elif final < 70:
            st.warning("⚠️ Moderate Stress")
        else:
            st.error("🚨 High Stress")
            
        # Suggestions (re-implemented local logic or fetch from backend? Local is faster here)
        st.info("💡 **Suggestions:**")
        if final < 40:
             st.write("- You are doing great! Keep maintaining this balance.")
        else:
             st.write("- Try deep breathing exercises (4-7-8 technique).")
             st.write("- Take a short break away from screens.")





st.subheader("Guided Demo")
st.caption("Follow the steps below. Each measurement runs on the backend and returns here.")

if "cam_rate" not in st.session_state:
    st.session_state.cam_rate = None
if "mic_rate" not in st.session_state:
    st.session_state.mic_rate = None
if "voice_score" not in st.session_state:
    st.session_state.voice_score = None

with st.container():
    st.markdown("### Step 1 — Camera (≈15s)")
    st.info("📸 **Camera will turn ON.** Sit facing the camera. Keep your upper body still. Good lighting helps.")
    if st.button("Start Camera Measurement"):
        with st.spinner("Detecting face and tracking chest motion..."):
            try:
                r = requests.get(f"{BACKEND_URL}/cam", timeout=600)
                data = r.json()
                st.session_state.cam_rate = data.get("camera_breath_rate", 0)
                
                if data.get("ok", False):
                    st.success(f"Camera breaths/min: {st.session_state.cam_rate}")
                    if "signal" in data and data["signal"]:
                        st.line_chart(data["signal"])
                        st.caption("Chest Motion Signal")
                else:
                    st.warning(f"Camera step returned 0. Details: {data.get('error','')}")
            except Exception as ex:
                st.session_state.cam_rate = 0
                st.error("Camera step failed.")
                st.caption(str(ex))

with st.container():
    st.markdown("### Step 2 — Microphone (≈12s)")
    st.info("🎙️ **Microphone will turn ON.** Remain quiet. Breathe normally close to the microphone.")
    if st.button("Start Microphone Measurement"):
        with st.spinner("Recording breathing audio..."):
            try:
                r = requests.get(f"{BACKEND_URL}/mic", timeout=600)
                data = r.json()
                st.session_state.mic_rate = data.get("mic_breath_rate", 0)
                
                if data.get("ok", False):
                    st.success(f"Microphone breaths/min: {st.session_state.mic_rate}")
                    if "signal" in data and data["signal"]:
                        st.line_chart(data["signal"])
                        st.caption("Breathing Audio Envelope")
                else:
                    st.warning(f"Mic step returned 0. Details: {data.get('error','')}")
            except Exception as ex:
                st.session_state.mic_rate = 0
                st.error("Microphone step failed.")
                st.caption(str(ex))

with st.container():
    st.markdown("### Step 3 — Voice (≈4s)")
    st.info("🗣️ **Microphone will record.** Read a short sentence in your normal voice.")
    if st.button("Record Voice Clip"):
        with st.spinner("Recording voice clip..."):
            try:
                r = requests.get(f"{BACKEND_URL}/voice", timeout=600)
                data = r.json()
                st.session_state.voice_score = data.get("voice_score", 0)
                
                if data.get("ok", False):
                    st.success(f"Voice stress score: {st.session_state.voice_score}")
                    if "signal" in data and data["signal"]:
                        st.line_chart(data["signal"])
                        st.caption("Voice Audio Waveform")
                else:
                    st.warning(f"Voice step returned 0. Details: {data.get('error','')}")
            except Exception as ex:
                st.session_state.voice_score = 0
                st.error("Voice step failed.")
                st.caption(str(ex))

st.markdown("---")
if st.button("Compute Final Score from Steps"):
    cam = st.session_state.cam_rate or 0
    mic = st.session_state.mic_rate or 0
    voice = st.session_state.voice_score or 0
    final, level = combine_scores(cam, mic, voice)
    
    st.subheader("Final FusionResult")
    st.caption("0.3×Camera + 0.3×Mic + 0.4×Voice")
    st.metric("Stress Score", final)
    st.write("Stress Level:", level)
    
    # Simple suggestions based on just the score for this manual button
    if final > 50:
         st.info("💡 **Tip:** Detecting elevated stress. Consider a breathing exercise.")
    else:
         st.success("💡 **Tip:** You seem calm. Keep it up!")

with st.expander("How this works", expanded=False):
    st.markdown(
        """
        1. Camera: detects face, tracks chest region motion to estimate breaths/min.
        2. Microphone: records quiet breathing audio, finds breath peaks to estimate breaths/min.
        3. Voice: records a short clip; energy, variability, and zero‑crossing rate form a stress score.
        4. Fusion: 0.3×camera + 0.3×mic + 0.4×voice → final stress score and level.
        """
    )

col_a, col_b = st.columns([3, 2])
with col_b:
    if st.button("Check Backend Connection"):
        try:
            r = requests.get(f"{BACKEND_URL}/", timeout=5)
            st.success(f"Backend OK at {BACKEND_URL} — {r.json().get('message','OK')}")
        except Exception as ex:
            st.error(f"Cannot reach backend at {BACKEND_URL}")
            st.caption(str(ex))


