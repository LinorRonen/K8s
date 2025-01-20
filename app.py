"""
Flask web app for fetching and displaying weather data from Visual Crossing API.
Allows users to enter a location and retrieve a 7-day weather forecast.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
import requests
from flask import Flask, render_template, request
from flask_caching import Cache


load_dotenv()

app = Flask(__name__)
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 3600
})

# Get Visual Crossing token from environment variables
VISUAL_CROSSING_TOKEN = os.getenv('VISUAL_CROSSING_TOKEN')


@app.template_filter('custom_format_date')
def custom_format_date(value, date_format='%A, %B %d, %Y'):
    """Format a date string to a specified format."""
    date = datetime.strptime(value, '%Y-%m-%d')
    return date.strftime(date_format)


def get_weather_data(location):
    """Fetch weather data from Visual Crossing API."""
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{location}?unitGroup=metric&key={VISUAL_CROSSING_TOKEN}&contentType="
        f"json"
    )

    response = requests.get(url, timeout=10)  # 10 seconds timeout
    return response.json() if response.status_code == 200 else None


@cache.cached(timeout=3600, key_prefix=lambda: request.form.get('location'))
@app.route('/', methods=['GET', 'POST'])
def index():
    """Render input form and handle weather data retrieval."""
    current_hour = datetime.now().strftime('%H:%M:%S')

    if request.method == 'POST':
        location = request.form.get('location')

        weather_data = get_weather_data(location)
        current_date = datetime.now().strftime('%d.%m.%Y')

        # Check if weather data is valid
        if not weather_data or 'days' not in weather_data:
            return render_template(
                'input.html',
                error="Invalid location.",
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
