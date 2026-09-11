import os
import uuid
from flask import Flask, render_template_string, request, jsonify
import boto3

app = Flask(__name__)

# ------------------- AWS DYNAMODB CONFIGURATION -------------------
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1") # Default: Mumbai Region
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "BUY_PROPERTY")

# Connect to AWS DynamoDB
try:
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    else:
        # Local system AWS credentials fallback
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    print("DynamoDB connection successful!")
except Exception as e:
    print("DynamoDB connection error:", e)

# ------------------- HTML TEMPLATE -------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DynamoDB JSON Inserter</title>
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
            background-color: #ff9900;
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
            background-color: #e68a00;
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
    <h2>DynamoDB me JSON Data Save Karein</h2>
    <p>Apna JSON data niche box me paste karein:</p>
    
    <form id="jsonForm">
        <textarea id="jsonData" placeholder='{\n  "property_name": "3 BHK Apartment",\n  "location": "Kolkata",\n  "price": "5500000"\n}' required></textarea>
        <button type="submit">Submit to DynamoDB</button>
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
        resultDiv.innerHTML = '<strong>Truti:</strong> Aapka JSON format sahi nahi hai!';
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
            resultDiv.innerHTML = `<strong>Safaltapoorvak Save Hua!</strong><br>Generated Property ID: <code>${data.inserted_id}</code>`;
        } else {
            resultDiv.className = 'error';
            resultDiv.innerHTML = `<strong>Truti:</strong> ${data.message}`;
        }
    } catch (error) {
        resultDiv.className = 'error';
        resultDiv.innerHTML = `<strong>Server Truti:</strong> Data bheja nahi ja saka.`;
    }

    resultDiv.style.display = 'block';
});
</script>

</body>
</html>
"""

# ------------------- ROUTES -------------------
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/insert', methods=['POST'])
def insert_data():
    try:
        data = request.get_json(force=True)
        
        if not data:
            return jsonify({'status': 'error', 'message': 'JSON khali hai ya amanya hai'}), 400

        # DynamoDB Primary Key Validation
        # Agar JSON me property_id nahi hai, toh ek unique UUID auto-generate ho jayega
        if 'property_id' not in data or not str(data['property_id']).strip():
            data['property_id'] = str(uuid.uuid4())
        else:
            data['property_id'] = str(data['property_id'])

        # DynamoDB me Item Insert karein
        table.put_item(Item=data)

        return jsonify({
            'status': 'success',
            'inserted_id': data['property_id']
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
