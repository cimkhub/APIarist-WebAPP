from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Process the Excel file
        df = pd.read_excel(file_path)
        os.remove(file_path)  # Delete the file after reading

        # Convert the DataFrame to JSON format
        result = []
        for index, row in df.iterrows():
            result.append({"Name": row[0], "Type": row[1]})

        return jsonify(result)

# Load the Excel file for API endpoints
API_DATA_FILE = 'alphavantage_api_endpoints.xlsx'
if not os.path.exists(API_DATA_FILE):
    raise FileNotFoundError(f"{API_DATA_FILE} does not exist")

df_api_data = pd.read_excel(API_DATA_FILE)

# Debugging: Print the column names and first few rows
print("Column names:", df_api_data.columns.tolist())
print("First few rows:")
print(df_api_data.head())

@app.route('/get_endpoints', methods=['POST'])
def get_endpoints():
    api_doc = request.json.get('api_doc')
    if not api_doc:
        return 'No API documentation provided', 400
    
    print(f"Received API documentation: {api_doc}")
    
    # Check the columns in the DataFrame
    if 'API' not in df_api_data.columns or 'API Endpoint' not in df_api_data.columns:
        print("Column names do not match")
        print("Actual columns:", df_api_data.columns.tolist())
        return 'Column names do not match', 400

    # Perform the query and provide debugging output
    matching_rows = df_api_data[df_api_data['API'] == api_doc]
    print("Matching rows:")
    print(matching_rows)

    endpoints = matching_rows['API Endpoint'].unique().tolist()
    print("Endpoints:", endpoints)
    return jsonify(endpoints)

@app.route('/get_parameters', methods=['POST'])
def get_parameters():
    data = request.json
    api_doc = data.get('api_doc')
    endpoint = data.get('endpoint')
    
    if not api_doc or not endpoint:
        return 'API documentation or endpoint not provided', 400
    
    print(f"Received API documentation: {api_doc}, Endpoint: {endpoint}")

    # Check the columns in the DataFrame
    if 'API' not in df_api_data.columns or 'API Endpoint' not in df_api_data.columns or 'API Parameter' not in df_api_data.columns:
        print("Column names do not match")
        print("Actual columns:", df_api_data.columns.tolist())
        return 'Column names do not match', 400

    # Perform the query and provide debugging output
    matching_row = df_api_data[(df_api_data['API'] == api_doc) & (df_api_data['API Endpoint'] == endpoint)].iloc[0]
    print("Matching row for parameters:")
    print(matching_row)

    parameters = eval(matching_row['API Parameter'])  # Convert the string representation of list of dicts to actual list of dicts
    formatted_parameters = [{'name': param['name'], 'required': param['required'], 'description': param['description']} for param in parameters]
    print("Formatted Parameters:", formatted_parameters)
    return jsonify(formatted_parameters)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
