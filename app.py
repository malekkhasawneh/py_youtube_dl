from flask import Flask, request, jsonify
import yt_dlp
import traceback
import os
import shutil

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'

# Ensure the download folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

download_url = {"url": None}

def clear_download_folder():
    """Clear the download folder before each download."""
    for filename in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def my_hook(d):
    if d['status'] == 'finished':
        print(f"Download finished. Filename: {d.get('filename')}")
    elif d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} at {d['_speed_str']} ETA: {d['_eta_str']}")

class MyLogger(object):
    def debug(self, msg):
        if 'Downloading webpage' in msg or 'Downloading video from' in msg:
            print(msg)
        if 'http' in msg:
            download_url["url"] = msg.split('http')[1].split(' ')[0]

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400

    url = data['url']
    print(f"Received URL: {url}")  # Debugging line

    try:
        clear_download_folder()
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'logger': MyLogger(),
            'progress_hooks': [my_hook]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_url = info_dict.get('url')
            print(f"Extracted Download URL: {video_url}")
            ydl.download([url])
            return jsonify({"message": "Video downloaded successfully", "download_url": video_url})
    except Exception as e:
        print("Error occurred: ")
        traceback.print_exc()  # Detailed error stack trace
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
