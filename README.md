@'
# Mental Wellness App

Short description here.

## How to run locally

1. Create virtualenv: `python -m venv venv`
2. Activate: `.\venv\Scripts\activate`
3. Install: `pip install -r backend/requirements.txt`
4. Run backend: `python backend\main.py`
5. Serve frontend locally: `python -m http.server` (from frontend folder)
'@ | Out-File -Encoding UTF8 README.md

git add README.md
git commit -m "Add README"
git push
