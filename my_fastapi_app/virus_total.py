import requests
from fastapi import HTTPException


# Function to scan a file using VirusTotal API
def scan_file(file_content: bytes):
    """
        This function scans a file using the VirusTotal API.

        Parameters:
        - file_content (bytes): The content of the file to be scanned.

        Workflow:
        1. Sets the API key and the endpoint URL for VirusTotal.
        2. Prepares the file for upload and sends it to the VirusTotal API.
        3. Handles any potential request exceptions, raising an HTTP error if the request fails.
        4. Processes the JSON response from VirusTotal to determine:
           - Whether the scan was successful.
           - The risk level based on the number of positive detections.
           - Any detected threats along with additional information.
        5. Returns a dictionary containing scan results, risk level, and threat details.
        """

    api_key = '2132174bf993ee04e7a15a46293e78921a7be848e1eeb5329b2467aa0a494b6f'
    url = 'https://www.virustotal.com/vtapi/v2/file/scan'
    files = {'file': ('file', file_content)}
    params = {'apikey': api_key}

    try:
        # Send the file to VirusTotal, ignoring SSL verification issues
        response = requests.post(url, files=files, params=params, verify=False)
        response.raise_for_status()  # Check for any HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise HTTPException(status_code=500, detail="Request to VirusTotal failed")

    result = response.json()

    # Check the response code from VirusTotal
    response_code = result.get('response_code', 0)  # Default to 0 if not present
    if response_code == 1:
        scan_status = "Scanned successfully"
    else:
        scan_status = "Error scanning the file"

    # Retrieve the score based on the number of positive detections
    score = result.get('positives', 0)

    # Assign a risk level based on the score
    if score == 0:
        risk_level = "insurance"
    elif score <= 5:
        risk_level = "suspect"
    else:
        risk_level = "uncertain"

    # Extract details about detected threats
    threat_details = result.get('scans', {})
    threat_info = {}

    # Loop through the scan engines and capture threat information
    for engine, data in threat_details.items():
        if data.get('detected', False):
            threat_info[engine] = {
                "threat": data.get('result', 'Unknown threat'),
                "version": data.get('version', 'Unknown version')
            }

    # Return the final scan result
    return {
        "scan_status": scan_status,  # Status of the scan (successful or error)
        "risk_level": risk_level,  # Risk level (safe, suspicious, unsafe)
        "score": score,  # Threat score from the scan
        "threat_details": threat_info  # Detailed information about detected threats
    }
