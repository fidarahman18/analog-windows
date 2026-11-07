import earthaccess
import os
from dotenv import load_dotenv

load_dotenv()

earthaccess.login()

# Search for ASTER GDEM v3 tiles (Example bounding box for Death Valley)
results = earthaccess.search_data(
    short_name='ASTGTM',
    bounding_box=(-117.2, 35.8, -116.2, 36.8),
    count=10
)

# Download the files to your local raw data folder
downloaded_files = earthaccess.download(results, "data/raw/")
print("Download complete!")