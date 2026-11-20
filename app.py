import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import streamlit as st
import google.generativeai as genai
import edge_tts
import asyncio
import os
import uuid
import textwrap
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ColorClip, CompositeVideoClip, AudioFileClip,
    VideoFileClip, ImageClip, CompositeAudioClip
)
import moviepy.video.fx.all as vfx

st.set_page_config(page_title="AI Pro Reel Maker | NAV OP LIVE", page_icon="🎬", layout="centered")

# ==========================================
# 👇 आपका WhatsApp नंबर और पासवर्ड लिस्ट 👇
# ==========================================
WHATSAPP_NUMBER = "917743066256"
VALID_PASSWORDS = ["NAV2026", "CLIENT01", "CLIENT02"]  # जितने चाहें उतने पासवर्ड जोड़ें

wa_msg = urllib.parse.quote("Bhai mujhe AI Reel Maker tool ka Access Password chahiye, rate kya hai?")
WA_LINK = f"https://wa.me/{WHATSAPP_NUMBER}?text={wa_msg}"

# --- कस्टम ब्रांडिंग और WhatsApp बटन CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');

.nav-brand-box {
    border: 2px solid #00f2fe;
    outline: 1px solid rgba(79, 172, 254, 0.5);
    outline-offset: 3px;
    border-radius: 10px;
    padding: 10px 16px;
    text-align: center;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
    box-shadow: 0 0 15px rgba(0, 242, 254, 0.35);
    margin: 12px 0;
}
.nav-brand-sub {
    font-family: 'Orbitron', sans-serif;
    font-size: 10px;
    letter-spacing: 3px;
    color: #94a3b8;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.nav-brand-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 16px;
    font-weight: 900;
    letter-spacing: 2px;
    background: linear-gradient(90deg, #00f2fe, #4facfe, #f093fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.wa-btn {
    display: block;
    width: 100%;
    text-align: center;
    background: linear-gradient(90deg, #25D366, #128C7E);
    color: white !important;
    font-weight: bold;
    font-size: 16px;
    padding: 12px 18px;
    border-radius: 10px;
    text-decoration: none;
    box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
    margin: 10px 0;
}
.wa-btn:hover {
    opacity: 0.92;
}
</style>
""", unsafe_allow_html=True)

BRAND_HTML = """
<div class="nav-brand-box">
    <div class="nav-brand-sub">POWERED BY</div>
    <div class="nav-brand-title">⚡ NAV OP LIVE ⚡</div>
</div>
"""

WA_CONTACT_HTML = f"""
<div style="background: rgba(30, 41, 59, 0.85); border: 1px solid #334155; border-radius: 12px; padding: 18px; text-align: center; margin-top: 15px;">
    <h4 style="margin: 0 0 8px 0; color: #f8fafc;">🔐 Access Password चाहिए?</h4>
    <p style="margin: 0 0 12px 0; color: #cbd5e1; font-size: 14px;">
        टूल का Access Password और प्लान रेट जानने के लिए <b>Naveen (NAV OP LIVE)</b> से संपर्क करें:<br>
        <span style="color: #38bdf8; font-weight: bold;">📱 WhatsApp: +91 7743066256</span>
    </p>
    <a href="{WA_LINK}" target="_blank" class="wa-btn">💬 WhatsApp पर मैसेज करें (NAV OP LIVE)</a>
</div>
"""

st.title("🎬 AI Instagram Pro Reel Maker")
st.write("अपना वीडियो या फोटो अपलोड करें—AI शायरी, वॉयसओवर, बैकग्राउंड म्यूजिक और कैप्शन के साथ पूरी रील बना देगा!")

# 1. साइडबार: लॉगिन और API Key
with st.sidebar:
    st.header("🔐 लॉगिन और सेटअप")
    user_pass = st.text_input("Access Password डालें", type="password")
    api_key = st.text_input("अपनी Gemini API Key डालें", type="password")
    st.markdown("[फ्री Gemini API Key यहाँ से निकालें](https://aistudio.google.com/app/apikey)")
    st.divider()
    st.markdown(f'<a href="{WA_LINK}" target="_blank" class="wa-btn" style="font-size:13px; padding:8px;">💬 Password के लिए WhatsApp करें</a>', unsafe_allow_html=True)
    st.markdown(BRAND_HTML, unsafe_allow_html=True)

if user_pass not in VALID_PASSWORDS:
    st.warning("कृपया साइडबार (ऊपर बाईं तरफ `>`) में सही Access Password डालें।")
    st.markdown(WA_CONTACT_HTML, unsafe_allow_html=True)
    st.markdown(BRAND_HTML, unsafe_allow_html=True)
    st.stop()

if not api_key:
    st.info("कृपया आगे बढ़ने के लिए अपनी Gemini API Key डालें।")
    st.markdown(BRAND_HTML, unsafe_allow_html=True)
    st.stop()

# 2. मुख्य इनपुट फॉर्म
topic = st.text_input("1. रील का टॉपिक या थीम लिखें:", placeholder="जैसे: जिम मोटिवेशन, मेहनत, या दर्द भरी शायरी")

col_a, col_b, col_c = st.columns(3)
with col_a:
    script_lang = st.selectbox("2. लिखने की भाषा:", ["Hinglish (English अक्षर)", "शुद्ध हिन्दी"])
with col_b:
    voice_choice = st.selectbox("3. आवाज़ (Voice):", ["हिन्दी - पुरुष (Madhur)", "हिन्दी - महिला (Swara)"])
with col_c:
    watermark = st.text_input("4. वॉटरमार्क:", placeholder="@your_instagram")

# 3. बैकग्राउंड मीडिया अपलोड
uploaded_bg = st.file_uploader(
    "5. बैकग्राउंड वीडियो या फोटो अपलोड करें (वैकल्पिक - खाली छोड़ने पर डार्क बैकग्राउंड लगेगा):",
    type=["mp4", "mov", "jpg", "jpeg", "png"]
)

uploaded_bgm = st.file_uploader(
    "6. बैकग्राउंड म्यूजिक MP3 अपलोड करें (वैकल्पिक):",
    type=["mp3", "wav"]
)

voice_map = {
    "हिन्दी - पुरुष (Madhur)": "hi-IN-MadhurNeural",
    "हिन्दी - महिला (Swara)": "hi-IN-SwaraNeural"
}

def fit_to_reel(clip, target_w=720, target_h=1280):
    """किसी भी साइज के वीडियो या फोटो को बिना पिचकाए 9:16 Reel साइज में फिट करता है"""
    clip_ratio = clip.w / clip.h
    target_ratio = target_w / target_h
    if clip_ratio > target_ratio:
        clip = clip.resize(height=target_h)
    else:
        clip = clip.resize(width=target_w)
    return clip.crop(x_center=clip.w / 2, y_center=clip.h / 2, width=target_w, height=target_h)

def create_text_overlay(display_text, wm_text, out_png, is_hinglish=True, w=720, h=1280):
    """बड़ा, साफ और बोल्ड टेक्स्ट ओवरले बनाता है"""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if is_hinglish:
        font_candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
    else:
        font_candidates = [
            "C:/Windows/Fonts/NirmalaB.ttf",
            "C:/Windows/Fonts/mangal.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]

    main_font = None
    for f_path in font_candidates:
        if os.path.exists(f_path):
            main_font = ImageFont.truetype(f_path, 48)
            wm_font = ImageFont.truetype(f_path, 30)
            break
    if main_font is None:
        main_font = ImageFont.load_default(size=44)
        wm_font = ImageFont.load_default(size=28)

    wrapped_lines = []
    for line in display_text.split("\n"):
        wrapped_lines.extend(textwrap.wrap(line, width=25))
    final_text = "\n".join(wrapped_lines)

    bbox = draw.multiline_textbbox((0, 0), final_text, font=main_font, align="center", spacing=18)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (w - tw) / 2
    y = (h - th) / 2

    draw.multiline_text((x + 4, y + 4), final_text, font=main_font, fill=(0, 0, 0, 240), align="center", spacing=18)
    draw.multiline_text((x, y), final_text, font=main_font, fill=(255, 255, 255, 255), align="center", spacing=18)

    if wm_text.strip():
        wbbox = draw.textbbox((0, 0), wm_text.strip(), font=wm_font)
        wx = (w - (wbbox[2] - wbbox[0])) / 2
        draw.text((wx, 1130), wm_text.strip(), font=wm_font, fill=(230, 230, 230, 235))

    img.save(out_png)

async def generate_voice(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice, rate="-5%")
    await communicate.save(output_path)

if st.button("🚀 प्रोफेशनल रील बनाएं", type="primary", use_container_width=True):
    if not topic:
        st.error("पहले रील का टॉपिक लिखें!")
    else:
        with st.spinner("AI स्क्रिप्ट लिख रहा है और आपकी रील रेंडर हो रही है... (20-30 सेकंड रुकें)"):
            temp_files = []
            clips_to_close = []
            try:
                genai.configure(api_key=api_key)
                is_hinglish = "Hinglish" in script_lang

                prompt = f"""
                Topic: {topic}
                Write an emotional, deep, and viral 2-line Shayari or motivational quote (20 to 30 words max) for an Instagram Reel.
                Provide:
                1. HINDI_VOICE: The exact Shayari in Devanagari Hindi script (for natural voiceover).
                2. HINGLISH_TEXT: The exact same Shayari written in Hinglish (Hindi words written in English/Roman alphabet).
                3. CAPTION: An engaging Instagram caption in {"Hinglish (English alphabet)" if is_hinglish else "Devanagari Hindi"} with a call-to-action and 12 viral hashtags.
                
                Format strictly as:
                HINDI_VOICE: <Devanagari Hindi>
                HINGLISH_TEXT: <Roman Hinglish>
                CAPTION: <caption and hashtags>
                """

                response = None
                last_error = None
                for m_name in ["gemini-3.0-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash"]:
                    try:
                        model = genai.GenerativeModel(m_name)
                        response = model.generate_content(prompt).text
                        break
                    except Exception as err:
                        last_error = err
                        continue

                if not response:
                    raise Exception(f"AI मॉडल उपलब्ध नहीं हुआ: {last_error}")

                voice_text = response.split("HINGLISH_TEXT:")[0].replace("HINDI_VOICE:", "").strip()
                rest = response.split("HINGLISH_TEXT:")[1]
                hinglish_text = rest.split("CAPTION:")[0].strip()
                caption_text = rest.split("CAPTION:")[1].strip()

                screen_text = hinglish_text if is_hinglish else voice_text

                uid = uuid.uuid4().hex[:8]
                voice_path = f"temp_voice_{uid}.mp3"
                text_png_path = f"temp_text_{uid}.png"
                video_path = f"temp_reel_{uid}.mp4"
                temp_files.extend([voice_path, text_png_path, video_path])

                # 1. नेचुरल हिंदी उच्चारण के लिए देवनागरी से वॉयसओवर
                asyncio.run(generate_voice(voice_text, voice_map[voice_choice], voice_path))
                voice_clip = AudioFileClip(voice_path)
                clips_to_close.append(voice_clip)
                duration = voice_clip.duration + 1.0

                # 2. ऑडियो मिक्सिंग
                if uploaded_bgm is not None:
                    bgm_path = f"temp_bgm_{uid}_{uploaded_bgm.name}"
                    temp_files.append(bgm_path)
                    with open(bgm_path, "wb") as f:
                        f.write(uploaded_bgm.getbuffer())
                    bgm_clip = AudioFileClip(bgm_path)
                    clips_to_close.append(bgm_clip)
                    if bgm_clip.duration < duration:
                        bgm_clip = vfx.audio_loop(bgm_clip, duration=duration)
                    else:
                        bgm_clip = bgm_clip.subclip(0, duration)
                    bgm_clip = bgm_clip.volumex(0.18)
                    final_audio = CompositeAudioClip([voice_clip, bgm_clip])
                else:
                    final_audio = voice_clip

                # 3. बैकग्राउंड विजुअल
                layers = []
                if uploaded_bg is not None:
                    bg_path = f"temp_bg_{uid}_{uploaded_bg.name}"
                    temp_files.append(bg_path)
                    with open(bg_path, "wb") as f:
                        f.write(uploaded_bg.getbuffer())
                    
                    ext = uploaded_bg.name.split(".")[-1].lower()
                    if ext in ["mp4", "mov"]:
                        raw_bg = VideoFileClip(bg_path).without_audio()
                        clips_to_close.append(raw_bg)
                        if raw_bg.duration < duration:
                            raw_bg = vfx.loop(raw_bg, duration=duration)
                        else:
                            raw_bg = raw_bg.subclip(0, duration)
                        bg_clip = fit_to_reel(raw_bg)
                    else:
                        raw_img = ImageClip(bg_path).set_duration(duration)
                        bg_clip = fit_to_reel(raw_img)
                    
                    layers.append(bg_clip)
                    dark_shade = ColorClip(size=(720, 1280), color=(0, 0, 0)).set_opacity(0.45).set_duration(duration)
                    layers.append(dark_shade)
                else:
                    layers.append(ColorClip(size=(720, 1280), color=(18, 18, 18), duration=duration))

                # 4. बड़ा और साफ टेक्स्ट लेयर
                create_text_overlay(screen_text, watermark, text_png_path, is_hinglish=is_hinglish)
                txt_layer = ImageClip(text_png_path).set_duration(duration)
                layers.append(txt_layer)

                final_video = CompositeVideoClip(layers).set_audio(final_audio)
                clips_to_close.append(final_video)
                final_video.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac", logger=None)

                with open(video_path, "rb") as f:
                    video_bytes = f.read()

                st.success("✅ आपकी प्रोफेशनल Instagram Reel तैयार है!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.video(video_bytes)
                    st.download_button(
                        label="⬇️ रील डाउनलोड करें (MP4)",
                        data=video_bytes,
                        file_name="pro_instagram_reel.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                with col2:
                    st.subheader("📋 वायरल कैप्शन & हैशटैग")
                    st.text_area("कॉपी करके Instagram पर पेस्ट करें:", value=caption_text, height=320)

            except Exception as e:
                st.error(f"एरर आया: {e}")
            finally:
                for c in clips_to_close:
                    try:
                        c.close()
                    except Exception:
                        pass
                for tf in temp_files:
                    try:
                        if os.path.exists(tf):
                            os.remove(tf)
                    except Exception:
                        pass

st.divider()
st.markdown(BRAND_HTML, unsafe_allow_html=True)