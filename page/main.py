from fastapi import FastAPI, File, UploadFile, HTTPException
from pymongo import MongoClient
import requests
from fastapi.middleware.cors import CORSMiddleware
import traceback

app = FastAPI()
# Added CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Connection to MongoDB Atlas
client = MongoClient(
    "mongodb+srv://shira8939:BUtKwXVCAmgCOucg@cluster0.fm3sl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['file_scanning_db']
files_collection = db['scanned_files']

# Function to scan a file using VirusTotal
def scan_file(file_content: bytes):
    api_key = '2132174bf993ee04e7a15a46293e78921a7be848e1eeb5329b2467aa0a494b6f'
    url = 'https://www.virustotal.com/vtapi/v2/file/scan'
    files = {'file': ('file', file_content)}
    params = {'apikey': api_key}
    try:
        # Ignoring SSL issues
        response = requests.post(url, files=files, params=params, verify=False)
        response.raise_for_status()
        # Check for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise HTTPException(status_code=500, detail="Request to VirusTotal failed")

    result = response.json()
    # Checking the response code from the VirusTotal API
    response_code = result.get('response_code', 0)  # Default is 0 in case there is no value
    if response_code == 1:
        scan_status = "Scanned successfully"
    else:
        scan_status = "Error scanning the file"

    score = result.get('positives', 0)  # Risk score from the API
    # Determination of risk level according to the scan score
    if score == 0:
        risk_level = "insurance"
    elif score <= 5:
        risk_level = "suspect"
    else:
        risk_level = "uncertain"
    # Collection of threat information
    threat_details = result.get('scans', {})  #It contains more information about scans
    threat_info = {}

    for engine, data in threat_details.items():
        if data.get('detected', False):
            threat_info[engine] = {
                "threat": data.get('result', 'Unknown threat'),
                "version": data.get('version', 'Unknown version')
            }

    return {
        "scan_status": scan_status,# Is the scan complete
        "risk_level": risk_level, # Risk level (safe, suspicious, unsafe)
        "score": score,  # The numerical score that indicates the threat level
        "threat_details": threat_info  # Details of the threats, if any
    }

# Path to upload file
@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Reading the contents of the file
        file_content = await file.read()
        # Scan the file
        scan_result = scan_file(file_content)
        # Saving the result in MongoDB
        file_data = {
            "filename": file.filename,
            "scan_result": scan_result,
            "file_size": len(file_content)
        }
        files_collection.insert_one(file_data)
        # Returning a result to the client
        return {
            "filename": file.filename,
            "scan_result": scan_result
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Path to display scanned files
@app.get("/files/")
def get_files():
    files = list(files_collection.find({}, {'_id': False}))
    return files


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
