from pymongo import MongoClient

# MongoDB connection to the 'file_scanning_db' database
client = MongoClient(
    "mongodb+srv://shira8939:BUtKwXVCAmgCOucg@cluster0.fm3sl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client['file_scanning_db']  # Select the 'file_scanning_db' database
files_collection = db['scanned_files']  # Collection where scanned files are stored
