from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongo import files_collection  # Importing the MongoDB connection
from virus_total import scan_file  # Importing the VirusTotal scan function
from fastapi import File, UploadFile, HTTPException
import traceback

app = FastAPI()

# Adding CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Route to upload a file
@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    """
        This function handles file uploads from the client.

        Parameters:
        - file (UploadFile): The uploaded file object from the client.

        Workflow:
        1. The function receives a file uploaded through an HTTP POST request.
        2. The content of the uploaded file is read asynchronously.
        3. The file is scanned for potential threats using VirusTotal via the `scan_file` function.
        4. The scan result, along with the filename and file size, is saved to a MongoDB collection.
        5. The scan result and file name are returned as a response to the client.

        If any exception occurs during the process, it is caught, logged, and an HTTP 500 error is raised.
        """
    try:
        # Check file size limit (32 MB)
        if file.file._file.size > 32 * 1024 * 1024:  # 32 MB limit
            raise HTTPException(status_code=413, detail="File too large, please upload a smaller file (max 32 MB).")
        # Read the content of the uploaded file
        file_content = await file.read()
        # Scan the file using VirusTotal
        scan_result = scan_file(file_content)
        # Store the result in MongoDB
        file_data = {
            "filename": file.filename,
            "scan_result": scan_result,
            "file_size": len(file_content)
        }
        files_collection.insert_one(file_data)
        # Return the scan result to the client
        return {
            "filename": file.filename,
            "scan_result": scan_result
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Route to display scanned files
@app.get("/files/")
def get_files():
    """
        This function retrieves a list of scanned files from the MongoDB collection.

        Workflow:
        1. It queries MongoDB to fetch all files that have been scanned, excluding the '_id' field.
        2. It converts the result into a list format.
        3. The list of scanned files is returned as a response to the client.
        """
    # Fetching all scanned files from MongoDB
    files = list(files_collection.find({}, {'_id': False}))  # Exclude '_id' field from the result
    return files

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
