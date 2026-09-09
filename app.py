import os
import json
from flask import Flask, render_template_string, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = "mongodb+srv://pawandevprasad8_db_user:12300pawandevprasad03112010@cluster0.xmjo7lc.mongodb.net/?appName=Cluster0"
DB_NAME = "BUY_PROPERTY_KOLKATA"
COLLECTION_NAME = "KOLKATA_LISTING"

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("MongoDB से कनेक्शन सफल रहा!")
except Exception as e:
    print("MongoDB कनेक्शन में त्रुटि:", e)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MongoDB JSON Inserter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 650px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f4f6f9;
        }
        .container {
            background: #ffffff;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        h2 {
            margin-top: 0;
            color: #333;
        }
        textarea {
            width: 100%;
            height: 220px;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-family: monospace;
            font-size: 14px;
            box-sizing: border-box;
            resize: vertical;
        }
        button {
            margin-top: 15px;
            background-color: #00684a;
            color: white;
            border: none;
            padding: 12px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            font-weight: bold;
        }
        button:hover {
            background-color: #005139;
        }
        #result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
            word-break: break-all;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>

<div class="container">
    <h2>MongoDB में JSON डेटा सेव करें</h2>
    <p>अपना JSON डेटा नीचे बॉक्स में पेस्ट करें:</p>
    
    <form id="jsonForm">
        <textarea id="jsonData" placeholder='{\n  "property_name": "3 BHK Apartment",\n  "location": "Kolkata",\n  "price": "5500000"\n}' required></textarea>
        <button type="submit">Submit to MongoDB</button>
    </form>

    <div id="result"></div>
</div>

<script>
document.getElementById('jsonForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const jsonText = document.getElementById('jsonData').value;
    const resultDiv = document.getElementById('result');
    
    try {
        JSON.parse(jsonText);
    } catch (err) {
        resultDiv.className = 'error';
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<strong>त्रुटि:</strong> आपका JSON फ़ॉर्मेट सही नहीं है!';
        return;
    }

    resultDiv.style.display = 'none';

    try {
        const response = await fetch('/insert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: jsonText
        });

        const data = await response.json();

        if (data.status === 'success') {
            resultDiv.className = 'success';
            resultDiv.innerHTML = `<strong>सफलतापूर्वक सेव हुआ!</strong><br>Generated Document ID: <code>${data.inserted_id}</code>`;
        } else {
            resultDiv.className = 'error';
            resultDiv.innerHTML = `<strong>त्रुटि:</strong> ${data.message}`;
        }
    } catch (error) {
        resultDiv.className = 'error';
        resultDiv.innerHTML = `<strong>सर्वर त्रुटि:</strong> डेटा भेजा नहीं जा सका।`;
    }

    resultDiv.style.display = 'block';
});
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/insert', methods=['POST'])
def insert_data():
    try:
        data = request.get_json(force=True)
        
        if not data:
            return jsonify({'status': 'error', 'message': 'JSON खाली है या अमान्य है'}), 400

        result = collection.insert_one(data)

        return jsonify({
            'status': 'success',
            'inserted_id': str(result.inserted_id)
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

