from flask import Flask, render_template, request, redirect, url_for, Response
from config import tasks_ref
from google.cloud.firestore import SERVER_TIMESTAMP
import json
import time
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Custom JSON encoder to handle Firestore timestamps
class FirestoreEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'timestamp'):  # Handle Firestore timestamps
            return datetime.fromtimestamp(obj.timestamp()).isoformat()
        return super().default(obj)

# Helper functions
def create_task(number, drinks, food, extra):
    """Create a new task in Firestore"""
    # Format drinks as a comma-separated string
    formatted_drinks = []
    for name, quantity in drinks.items():
        if quantity and int(quantity) > 0:
            item_name = name.replace('_', ' ').title()
            # Remove 'Juice' from juice items
            item_name = item_name.replace(' Juice', '')
            formatted_drinks.append(f"{quantity}x {item_name}")
    
    drinks_str = ', '.join(formatted_drinks) if formatted_drinks else 'N/A'
    
    task_data = {
        'number': number,
        'drinks': drinks_str,
        'extra': extra if extra else 'N/A',
        'timestamp': SERVER_TIMESTAMP
    }
    
    doc_ref = tasks_ref.document()
    doc_ref.set(task_data)
    return doc_ref.id

def get_all_tasks():
    """Retrieve all tasks from Firestore"""
    tasks = []
    try:
        for doc in tasks_ref.order_by('timestamp', direction='DESCENDING').stream():
            task = doc.to_dict()
            task['id'] = doc.id
            # Convert timestamp to string if it exists
            if 'timestamp' in task and task['timestamp']:
                try:
                    task['timestamp'] = datetime.fromtimestamp(task['timestamp'].timestamp()).isoformat()
                except AttributeError:
                    task['timestamp'] = datetime.now().isoformat()  # Fallback timestamp
            tasks.append(task)
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []
    return tasks

# Routes
@app.route('/')
def home():
    return redirect(url_for('requestor'))

@app.route('/requestor', methods=['GET', 'POST'])
def requestor():
    number = request.args.get('num', '')
    
    if request.method == 'POST':
        # Get all form items with non-zero quantities
        drinks = {k: v for k, v in request.form.items() 
                 if k not in ['number', 'extra'] and v.isdigit() and int(v) > 0}
        
        if number and drinks:
            create_task(
                number,
                drinks,
                None,
                request.form.get('extra')
            )
        return redirect(url_for('requestor', num=number))
    
    return render_template('requestor.html', number=number)

@app.route('/supplier', methods=['GET', 'POST'])
def supplier():
    try:
        if request.method == 'POST':
            task_id = request.form.get('task_id')
            if task_id:
                tasks_ref.document(task_id).delete()
            return redirect(url_for('supplier'))
        
        tasks = get_all_tasks()
        return render_template('supplier.html', tasks=tasks)
    except Exception as e:
        print(f"Error in supplier route: {e}")
        return render_template('supplier.html', tasks=[])

@app.route('/stream')
def stream():
    """Server-Sent Events endpoint"""
    def event_stream():
        queue = []
        
        def on_snapshot(doc_snapshot, changes, read_time):
            try:
                # Add the updated tasks to the queue
                tasks = get_all_tasks()
                queue.append(tasks)
            except Exception as e:
                print(f"Error in snapshot listener: {e}")
        
        # Create a real-time listener
        doc_watch = tasks_ref.on_snapshot(on_snapshot)
        
        while True:
            try:
                if queue:
                    tasks = queue.pop(0)
                    yield f"data: {json.dumps(tasks, cls=FirestoreEncoder)}\n\n"
                time.sleep(0.5)
            except Exception as e:
                print(f"Error in event stream: {e}")
                time.sleep(1)
            
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
