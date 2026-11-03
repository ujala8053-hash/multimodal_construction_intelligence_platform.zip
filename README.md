# Multimodal Construction Intelligence Platform

A lightweight, runnable Flask prototype for construction planning and preliminary decision support. It is intentionally kept small (no large ML weights or datasets) so it is easy to run and upload to GitHub.

## Features
- **Image-based analysis:** upload a construction/site image; checks image dimensions, brightness, contrast, and dominant colour cues.
- **Construction planning:** creates a simple stage-by-stage schedule from a target duration and floor count.
- **Cost estimation / valuation support:** illustrative cost breakdown by project type, area, and floors in INR.
- **AI intelligence / advisory assistant:** rule-based construction guidance for safety, estimates, schedules, materials, and image analysis.
- **Web interface:** responsive dashboard with cards, forms, result panels, and upload preview.

## Important limitation
This is a demonstration prototype, not a certified engineering tool. Image analysis uses basic image statistics, not a trained multimodal AI model. It cannot detect or rule out structural defects or certify a building's safety. Cost rates are illustrative; replace them with validated local rates. Seek qualified professional review for structural, code, and safety decisions.

## Requirements
- Python 3.10 or newer
- pip

## Run on Windows (VS Code terminal)
1. Extract the ZIP.
2. Open the extracted `multimodal_construction_intelligence_platform` folder in VS Code.
3. Create and activate a virtual environment (optional but recommended):

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   py app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

## GitHub upload tips
Do not upload `.venv`, `__pycache__`, `.env`, or private credentials. The source project is small; the app creates `static/uploads` at runtime.

## Project workflow
Requirements & setup → image review → planning & estimate → advisory assistant → professional verification and handover.
