import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

# Check if running on Render
if os.getenv('RENDER'):
    # Use JSON string from environment variable
    cred_dict = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    cred = credentials.Certificate(cred_dict)
else:
    # Use local file path
    cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))

# Initialize Firebase Admin with your service account credentials
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()
tasks_ref = db.collection('tasks') 