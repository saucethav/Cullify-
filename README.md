# Cullify

Cullify is a photo culling tool focused on speed, trust, and a clean workflow. It detects unreadable files, blur, near-duplicates, and closed eyes.

## Current repo layout (simplified)
- app.py — Streamlit prototype UI
- cullify.py — CLI runner
- filters/ — blur, duplicates, eyes detection
- models/ — face cascade (haarcascade_frontalface_default.xml)
- bad/, filtered/, runs/ — local output/test folders (ignored)
- .gitignore — keeps local data and caches out of git

## Quick start

1) Create and activate a virtual environment
- macOS/Linux:
  - python3 -m venv .venv
  - source .venv/bin/activate
- Windows (PowerShell):
  - py -m venv .venv
  - .venv\Scripts\Activate.ps1

2) Install dependencies
- pip install -r requirements.txt

3) Run the Streamlit app (prototype)
- streamlit run app.py

4) Or run the CLI
- python cullify.py --input /path/to/images --output /path/to/output

## Notes
- The filters use OpenCV, Pillow, and MediaPipe (for eyes). Make sure your environment has these installed (see requirements.txt).
- The models/ folder should contain haarcascade_frontalface_default.xml.
- Local data folders like runs/, bad/, filtered/ are ignored by git to keep the repo clean.