import streamlit as st
import os
import shutil
from datetime import datetime
from filters.blur import is_blurry
from filters.eyes import eyes_closed
from filters.duplicates import find_duplicates
import cv2
import zipfile

st.set_page_config(page_title="Cullify", layout="wide")

# Config
st.sidebar.header("Threshold Settings")

BLUR_THRESHOLD = st.sidebar.slider(
    "Blur Threshold",
    min_value = 10.0,
    max_value = 500.0,
    value = 100.0,
    step = 10.0,
    help = "Lower = stricter blur detection. Higher = more lenient."
)

EYES_THRESHOLD = st.sidebar.slider(
    "Eye Aspect Ratio (EAR) Threshold",
    min_value = 0.1,
    max_value = 0.4,
    value = 0.26,
    step = 0.01,
    help = "Lower = only fully shut eyes flagged. Higher = more sensitive."
)


st.title("Cullify — Smart Photo Filter")

# File upload
uploaded_files = st.file_uploader("Upload your photos (JPG, PNG)", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

if uploaded_files:
    # Setup folders
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir = f"runs/{timestamp}"
    input_dir = os.path.join(base_dir, "input")
    good_dir = os.path.join(base_dir, "filtered")
    bad_dir = os.path.join(base_dir, "bad")
    os.makedirs(input_dir, exist_ok = True)
    os.makedirs(good_dir, exist_ok = True)
    os.makedirs(bad_dir, exist_ok = True)

    # Save uploaded images to input folder
    for file in uploaded_files:
        with open(os.path.join(input_dir, file.name), "wb") as f:
            f.write(file.getbuffer())

    st.info("Processing your photos...")

    # Detect duplicates first
    duplicates = find_duplicates(input_dir)

    # Process images
    blurry, closed, duplicate, good = [], [], [], []
    
    rejection_reasons = {}  # filename → list of reasons

    for filename in os.listdir(input_dir):
        path = os.path.join(input_dir, filename)
        is_dup = filename in duplicates
        is_blur = is_blurry(path, threshold=BLUR_THRESHOLD)
        is_closed = eyes_closed(path, eye_threshold=EYES_THRESHOLD)

        reasons = []

        if is_dup:
            duplicate.append(filename)
            reasons.append("Duplicate")
        if is_blur:
            blurry.append(filename)
            reasons.append("Blurry")
        if is_closed:
            closed.append(filename)
            reasons.append("Eyes Closed")

        if reasons:
            rejection_reasons[filename] = reasons
            target = os.path.join(bad_dir, filename)
        else:
            good.append(filename)
            target = os.path.join(good_dir, filename)


        cv2.imwrite(target, cv2.imread(path))

    # Summary
    st.success("Done!")
    st.subheader("Cullify Summary")
    st.markdown(f"""
    - **Total images**: {len(uploaded_files)}
    - **Blurry**: {len(blurry)}
    - **Eyes closed**: {len(closed)}
    - **Duplicates**: {len(duplicate)}
    - **Filtered (good)**: {len(good)}
    """)

    # Show good photos
    with st.expander("🖼️ Preview Good Photos"):
        cols = st.columns(4)
        for i, filename in enumerate(good):
            img = cv2.imread(os.path.join(good_dir, filename))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cols[i % 4].image(img, caption = filename, use_container_width = True)

    #Show bad photos
    with st.expander("🗑️ Preview Bad Photos"):
        st.markdown("**Filter by reason:**")
        show_blurry = st.checkbox("Blurry", value=True)
        show_closed = st.checkbox("Eyes Closed", value=True)
        show_duplicates = st.checkbox("Duplicates", value=True)

        # Map user selections to logic
        selected_reasons = set()
        if show_blurry:
            selected_reasons.add("Blurry")
        if show_closed:
            selected_reasons.add("Eyes Closed")
        if show_duplicates:
            selected_reasons.add("Duplicate")

        cols = st.columns(4)
        i = 0
        for filename, reasons in rejection_reasons.items():
            if not selected_reasons.intersection(reasons):
                continue  # Skip if this photo doesn't match selected filters

            img_path = os.path.join(bad_dir, filename)
            if os.path.exists(img_path):
                img = cv2.imread(img_path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                reason_str = ", ".join(reasons)
                cols[i % 4].image(img, caption=f"{filename}\n❌ {reason_str}", use_container_width=True)
                i += 1




    # Zip export
    zip_path = os.path.join(base_dir, "Cullify_Filtered.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in good:
            file_path = os.path.join(good_dir, file)
            zipf.write(file_path, arcname=file)

    with open(zip_path, "rb") as f:
        st.download_button("📦 Download Filtered Photos", f, file_name="Cullify_Filtered.zip")
