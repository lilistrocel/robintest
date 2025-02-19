import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

# Get credentials from environment variable
cred_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
cred_dict = json.loads(cred_json)  # Parse the JSON string into a dictionary
cred = credentials.Certificate(cred_dict)  # Use the dictionary directly

# Initialize Firebase Admin
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()
tasks_ref = db.collection('tasks') 