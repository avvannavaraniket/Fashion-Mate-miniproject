# app.py
import base64
from typing import Any, Dict, Optional

import streamlit as st

# -----------------------------
# Config & constants
# -----------------------------
st.set_page_config(
    page_title="FashionMate · AI Personal Stylist",
    page_icon="🧥",
    layout="centered",
)

OCCASION_MIN_LENGTH = 5
OCCASION_MAX_LENGTH = 300
PREFERENCES_MAX_LENGTH = 200

SUGGESTED_OCCASIONS = [
    "Casual Coffee Date",
    "Summer Wedding Guest",
    "Tech Job Interview",
    "Weekend Brunch",
    "Gallery Opening",
    "Beach Vacation",
]

GENDER_OPTIONS = ["Female", "Male", "Non-Binary"]


# -----------------------------
# Optional: real API integration
# -----------------------------
def get_outfit_recommendation(
    occasion: str,
    gender: str,
    preferences: str,
    image: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Replace this with your real Gemini / backend call.
    `image` will look like: {"inlineData": {"data": <base64>, "mimeType": <mimetype>}}
    """
    # TODO: integrate your actual model/service here
    # For now, just return a fake structured response for display.
    return {
        "occasion": occasion,
        "gender": gender,
        "preferences": preferences,
        "has_image": image is not None,
        "summary": "Here’s a sample outfit suggestion. Replace this with real model output.",
        "outfit": {
            "top": "Crisp white shirt",
            "bottom": "High-waisted tailored trousers",
            "shoes": "Minimal leather sneakers",
            "accessories": ["Simple silver watch", "Slim belt"],
        },
    }


# -----------------------------
# Helpers
# -----------------------------
def init_state():
    defaults = {
        "result": None,
        "error": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def validate_fields(
    occasion: str,
    gender: str,
    preferences: str,
    has_image: bool,
) -> Dict[str, str]:
    errors = {"occasion": "", "gender": "", "preferences": ""}

    # Occasion
    trimmed = occasion.strip()
    if not trimmed and not has_image:
        errors["occasion"] = "Please describe the occasion or upload a photo."
    elif trimmed and len(trimmed) < OCCASION_MIN_LENGTH and not has_image:
        errors["occasion"] = f"Add at least {OCCASION_MIN_LENGTH} characters."
    elif len(occasion) > OCCASION_MAX_LENGTH:
        errors["occasion"] = f"Limit to {OCCASION_MAX_LENGTH} characters."

    # Gender
    if not gender.strip():
        errors["gender"] = "Please select a style focus."

    # Preferences
    if len(preferences) > PREFERENCES_MAX_LENGTH:
        errors["preferences"] = f"Limit to {PREFERENCES_MAX_LENGTH} characters."
    elif len(preferences) > 0 and not any(ch.isalnum() for ch in preferences):
        errors["preferences"] = "Please include valid text."

    return errors


def encode_image(file) -> Optional[Dict[str, Any]]:
    if file is None:
        return None
    file_bytes = file.read()
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    return {
        "inlineData": {
            "data": encoded,
            "mimeType": file.type,
        }
    }


def render_result(result: Any):
    st.markdown("### Your Curated Look ✨")
    if isinstance(result, dict):
        # Show a nice summary if present
        summary = result.get("summary")
        if summary:
            st.markdown(f"**Summary**: {summary}")

        st.markdown("#### Details")
        st.json(result)
    else:
        st.markdown(result)


# -----------------------------
# Global styling (light / pinteresty)
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #fef3c7 0, #faf5ff 25%, #f5f5f4 55%, #ffffff 100%);
        color: #1c1917;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }
    textarea, input, .stTextInput input {
        color: #1c1917 !important;
    }
    .pill-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.35);
        background: rgba(255, 255, 255, 0.65);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #6b7280;
    }
    .hero-title {
        font-family: "DM Serif Display", "Playfair Display", Georgia, "Times New Roman", serif;
        font-size: clamp(2.8rem, 3.5vw + 1rem, 4rem);
        line-height: 1.1;
        color: #111827;
    }
    .card {
        border-radius: 32px;
        padding: 24px;
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.7);
        box-shadow: 0 24px 50px -24px rgba(15, 23, 42, 0.22);
    }
    .chip {
        padding: 8px 16px;
        border-radius: 999px;
        background: rgba(255,255,255,0.80);
        border: 1px solid rgba(226, 232, 240, 0.9);
        font-size: 12px;
        font-weight: 600;
        color: #4b5563;
        cursor: pointer;
        transition: all 150ms ease-out;
    }
    .chip:hover {
        background: #ffffff;
        border-color: #d1d5db;
        color: #111827;
        box-shadow: 0 6px 14px -10px rgba(15, 23, 42, 0.7);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# App
# -----------------------------
init_state()

# Header
col_left, col_right = st.columns([3, 1], gap="large")

with col_left:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:12px; margin-bottom: 0.75rem;">
            <div style="
                width:40px;height:40px;border-radius:999px;
                background:#0f172a;color:white;
                display:flex;align-items:center;justify-content:center;
                box-shadow:0 10px 30px -12px rgba(15,23,42,0.7);
                font-size:20px;
            ">🧥</div>
            <div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 26px; font-weight:700;">FashionMate</div>
                <div style="font-size: 12px; color:#6b7280; text-transform:uppercase; letter-spacing:0.16em;">AI personal stylist</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_right:
    if st.session_state.result is not None:
        if st.button("New Search", use_container_width=True):
            st.session_state.result = None
            st.session_state.error = None
            st.experimental_rerun()

st.markdown("---")

# If no result yet, show input UI; otherwise show result
if st.session_state.result is None:
    # Hero section
    st.markdown(
        """
        <div style="text-align:center;margin: 2rem 0 1rem 0;">
            <div class="pill-badge">AI Personal Stylist</div>
            <h1 class="hero-title" style="margin-top: 1.5rem;">
                What is the<br/> <span style="font-style:italic;">occasion?</span>
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)

    with st.form("stylist_form", clear_on_submit=False):
        # Occasion + image
        st.markdown("##### Describe the Event / Request")
        occasion = st.text_area(
            "Occasion",
            label_visibility="collapsed",
            placeholder="e.g. A gallery opening in Soho, minimal but chic...",
            height=120,
            max_chars=OCCASION_MAX_LENGTH,
        )
        st.caption(f"{len(occasion)}/{OCCASION_MAX_LENGTH} characters")

        img_col, txt_col = st.columns([1, 2], gap="medium")

        with img_col:
            uploaded_image = st.file_uploader(
                "Upload a photo (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                label_visibility="visible",
            )
            if uploaded_image is not None:
                st.image(uploaded_image, caption="Upload preview", use_column_width=True)

        # Gender
        with txt_col:
            st.markdown("##### Style Focus")
            gender = st.radio(
                "Style Focus",
                options=GENDER_OPTIONS,
                horizontal=True,
                label_visibility="collapsed",
            )

        # Preferences
        st.markdown("##### Style Profile (Optional)")
        preferences = st.text_input(
            "Style Profile",
            value="",
            max_chars=PREFERENCES_MAX_LENGTH,
            placeholder="e.g. Minimal style, low budget, dislike neon...",
            label_visibility="collapsed",
        )
        st.caption(f"{len(preferences)}/{PREFERENCES_MAX_LENGTH} characters")

        # Submit
        submitted = st.form_submit_button(
            "Curate My Look",
            use_container_width=True,
        )

        # Handle submit
        if submitted:
            image_payload = encode_image(uploaded_image)
            errors = validate_fields(
                occasion=occasion,
                gender=gender,
                preferences=preferences,
                has_image=image_payload is not None,
            )

            # Display errors (similar to your validationErrors)
            has_any_error = False
            for field, msg in errors.items():
                if msg:
                    has_any_error = True
                    st.error(f"{field.capitalize()}: {msg}")

            if not has_any_error:
                try:
                    with st.spinner("Curating Style..."):
                        result = get_outfit_recommendation(
                            occasion=occasion,
                            gender=gender,
                            preferences=preferences,
                            image=image_payload,
                        )
                    st.session_state.result = result
                    st.session_state.error = None
                    st.experimental_rerun()
                except Exception as e:
                    st.session_state.error = str(e)

    st.markdown("</div>", unsafe_allow_html=True)

    # Suggestions chips
    st.markdown("###### Or pick a quick occasion:")
    chip_cols = st.columns(3)
    for idx, text in enumerate(SUGGESTED_OCCASIONS):
        col = chip_cols[idx % 3]
        with col:
            if st.button(text, key=f"suggestion_{idx}"):
                # Pre-fill the occasion field with this text
                st.session_state["stylist_form-Occasion"] = text  # Streamlit's internal key
                st.experimental_rerun()

else:
    # Result view
    if st.session_state.error:
        st.error(st.session_state.error)

    render_result(st.session_state.result)
    st.markdown("---")
    if st.button("Start Another Look", use_container_width=True):
        st.session_state.result = None
        st.session_state.error = None
        st.experimental_rerun()