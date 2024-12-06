import requests
import tarfile
import os
import shutil

def download_geoip_database():
    # URL for the free GeoLite2 City database
    url = "https://raw.githubusercontent.com/P3TERX/GeoLite.mmdb/download/GeoLite2-City.mmdb"
    
    print("Downloading GeoIP database...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the database file
        with open("GeoLite2-City.mmdb", "wb") as f:
            f.write(response.content)
            
        print("GeoIP database downloaded successfully!")
        
    except Exception as e:
        print(f"Error downloading GeoIP database: {e}")
        print("The geolocation features will be disabled.")

if __name__ == "__main__":
    download_geoip_database()
