import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin._apps import get_app

# Load environment variables
load_dotenv()

def initialize_firebase():
    try:
        # Check if already initialized
        app = get_app()
    except ValueError:
        # Initialize if not already done
        cred = credentials.Certificate('firebase-credentials.json')
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

# Get Firestore client
db = initialize_firebase()
tasks_ref = db.collection('tasks') 