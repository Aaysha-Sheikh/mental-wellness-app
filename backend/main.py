

import os
from flask import Flask, redirect, request, session, url_for, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# --------------------------
# Load env
# --------------------------
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --------------------------
# Flask
# --------------------------
app = Flask(__name__)
app.secret_key = "supersecret"

# --------------------------
# Firebase
# --------------------------
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --------------------------
# Gemini
# --------------------------
genai.configure(api_key=GEMINI_API_KEY)

# --------------------------
# OAuth Setup
# --------------------------
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# --------------------------
# OAuth Routes
# --------------------------

@app.route("/authorize")
def authorize():
    """Start OAuth flow with YouTube and save Firebase UID"""
    uid = request.args.get("uid")
    if not uid:
        return "UID missing", 400

    # Save UID in session
    session["firebase_uid"] = uid

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    session["state"] = state
    return redirect(auth_url)


# @app.route("/authorize")
# def authorize():
#     uid = request.args.get("uid")
#     if not uid:
#         return "No UID provided", 400
#     session["firebase_uid"] = uid  # save in session

#     flow = Flow.from_client_config(
#         {
#             "web": {
#                 "client_id": CLIENT_ID,
#                 "client_secret": CLIENT_SECRET,
#                 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                 "token_uri": "https://oauth2.googleapis.com/token",
#                 "redirect_uris": [REDIRECT_URI]
#             }
#         },
#         scopes=SCOPES,
#         redirect_uri=REDIRECT_URI
#     )
#     auth_url, state = flow.authorization_url(
#         access_type="offline", include_granted_scopes="true", prompt="consent"
#     )
#     session["state"] = state
#     return redirect(auth_url)

@app.route("/oauth2callback")
def oauth2callback():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session["credentials"] = creds_to_dict(creds)

    # Save to Firestore
    user_id = session.get("firebase_uid")
    if user_id:
        db.collection("youtube_tokens").document(user_id).set(session["credentials"])

    return redirect("/analyze")

# --------------------------
# Analyze Route (Improved)
# --------------------------
@app.route("/analyze")
def analyze():
    """Fetch YouTube feed + analyze with Gemini"""
    user_id = session.get("firebase_uid")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    # Load credentials from Firestore if available
    doc = db.collection("youtube_tokens").document(user_id).get()
    if doc.exists:
        creds_data = doc.to_dict()
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    elif "credentials" in session:
        creds = Credentials.from_authorized_user_info(session["credentials"], SCOPES)
    else:
        return jsonify({"error": "No YouTube connection"}), 403

    # Refresh if expired
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        db.collection("youtube_tokens").document(user_id).set(creds_to_dict(creds))

    # Call YouTube API
    youtube = build("youtube", "v3", credentials=creds)
    try:
        response = youtube.activities().list(
            part="snippet,contentDetails", home=True, maxResults=10
        ).execute()
        items = response.get("items", [])
        feed_texts = [item["snippet"].get("title", "") for item in items if "snippet" in item]
    except Exception as e:
        print("YouTube API error:", e)
        feed_texts = []

    # If feed is empty, use default test videos
    if not feed_texts:
        feed_texts = [
            "Meditation for stress relief",
            "10-minute workout",
            "Mindfulness tips for anxiety",
            "Healthy recipes for mental wellness",
            "Gratitude journaling ideas"
        ]

    # Send to Gemini
    model = genai.GenerativeModel("gemini-1.5-flash")
    analysis = model.generate_content(
        f"Analyze this YouTube feed for mental wellness signals: {feed_texts}"
    )

    return jsonify({"feed": feed_texts, "analysis": analysis.text})

@app.route("/generate_from_analysis", methods=["POST"])
def generate_from_analysis():
    """
    Generate story or image based on previous YouTube analysis
    Request JSON: { "type": "story" or "image", "analysis": "..." }
    """
    data = request.get_json()
    if not data or "analysis" not in data or "type" not in data:
        return {"error": "Invalid request"}, 400

    analysis = data["analysis"]
    gen_type = data["type"]

    if gen_type == "story":
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"Based on this YouTube analysis, create a short story promoting positive mental wellness:\n{analysis}"
        )
        return {"result": response.text}

    elif gen_type == "image":
        image = genai.images.generate(
            prompt=f"Create an illustration representing the following mental wellness analysis:\n{analysis}",
            size="1024x1024"
        )
        return {"result": image[0].url}

    else:
        return {"error": "Invalid type"}, 400



# --------------------------
# Helper
# --------------------------
def creds_to_dict(creds):
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes)
    }



# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
