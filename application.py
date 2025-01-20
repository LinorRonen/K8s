import os
import boto3
from datetime import datetime
from dotenv import load_dotenv
import requests
from flask import Flask, render_template, request, send_file, jsonify
from flask_caching import Cache

load_dotenv()

app = Flask(__name__)
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 3600
})

AWS_BUCKET_NAME = 'weather-app-linorg-bucket'
AWS_REGION = 'eu-north-1'
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

s3_client = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)


DOWNLOAD_DIR = os.path.expanduser("~/Desktop")  

VISUAL_CROSSING_TOKEN = os.getenv('VISUAL_CROSSING_TOKEN')


@app.template_filter('custom_format_date')
def custom_format_date(value, date_format='%A, %B %d, %Y'):
    """Format a date string to a specified format."""
    date = datetime.strptime(value, '%Y-%m-%d')
    return date.strftime(date_format)


def get_weather_data(location):
    """Fetch weather data from Visual Crossing API."""
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}?unitGroup=metric&key={VISUAL_CROSSING_TOKEN}&contentType=json"
    )

    response = requests.get(url, timeout=10)  # 10 seconds timeout
    return response.json() if response.status_code == 200 else None


@app.route('/download-sky-image', methods=['GET'])
def download_sky_image():
    """Download the sky image from S3 to the user's desktop."""
    image_name = 'background.png'  
    local_path = os.path.join(DOWNLOAD_DIR, image_name)

    try:
    
        s3_client.download_file(Bucket=AWS_BUCKET_NAME, Key=image_name, Filename=local_path)
        print(f"Image downloaded to: {local_path}")

        
        return send_file(local_path, as_attachment=True)
    except Exception as e:
        print(f"Error downloading image: {e}")
        return jsonify({'error': 'Failed to download the image.'}), 500


@cache.cached(timeout=3600, key_prefix=lambda: request.form.get('location'))
@app.route('/', methods=['GET', 'POST'])
def index():
    """Render input form and handle weather data retrieval."""
    current_hour = datetime.now().strftime('%H:%M:%S')

    if request.method == 'POST':
        location = request.form.get('location')

        weather_data = get_weather_data(location)
        current_date = datetime.now().strftime('%d.%m.%Y')

        if not weather_data or 'days' not in weather_data:
            error_message = "Invalid location. No weather data found."
            return render_template(
                'input.html',
                error=error_message,  
                current_hour=current_hour
            )

        
        return render_template(
            'result.html',
            weather_data=weather_data,
            current_date=current_date,
            success="Weather data retrieved successfully!",
            current_hour=current_hour
        )

    return render_template('input.html', current_hour=current_hour)


if __name__ == '__main__':
    app.run(debug=True, port=5002)
