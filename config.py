import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

# Initialize Firebase Admin with your service account credentials
cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()
tasks_ref = db.collection('tasks') 