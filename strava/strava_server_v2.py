from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, send_file, jsonify
import requests
import os
import datetime
import json
from configparser import ConfigParser
from urllib.parse import urlencode
from dateutil import parser
from datetime import timedelta
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
CONFIG_FILE = 'strava_config.ini'
TOKEN_FILE = 'strava_token.json'
ACTIVITIES_DIR = 'strava_activities'
POLYLINES_FILE = os.path.join(ACTIVITIES_DIR, 'activity_polylines.json')
ACTIVITIES_DIR = 'strava_activities'
os.makedirs(ACTIVITIES_DIR, exist_ok=True)

# Default settings
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100

class StravaAPI:
    def __init__(self):
        self.config = self._load_config()
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self._load_tokens()
        
    def _load_config(self):
        """Load configuration from file"""
        config = ConfigParser()
        if not os.path.exists(CONFIG_FILE):
            config['STRAVA'] = {
                'client_id': 'YOUR_CLIENT_ID',
                'client_secret': 'YOUR_CLIENT_SECRET',
                'redirect_uri': 'http://localhost:5000/authorized'
            }
            with open(CONFIG_FILE, 'w') as f:
                config.write(f)
            print(f"Please fill in your Strava API credentials in {CONFIG_FILE}")
            return config['STRAVA']
        
        config.read(CONFIG_FILE)
        return config['STRAVA']
    
    def _load_tokens(self):
        """Load tokens from file if they exist"""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                tokens = json.load(f)
                self.access_token = tokens.get('access_token')
                self.refresh_token = tokens.get('refresh_token')
                self.token_expires_at = tokens.get('expires_at')
                
                if self.token_expires_at and datetime.datetime.now().timestamp() > self.token_expires_at:
                    self._refresh_token()
    
    def _save_tokens(self, response):
        """Save tokens to file"""
        self.access_token = response['access_token']
        self.refresh_token = response['refresh_token']
        self.token_expires_at = response['expires_at']
        
        with open(TOKEN_FILE, 'w') as f:
            json.dump({
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expires_at': self.token_expires_at
            }, f)
    
    def _refresh_token(self):
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            return False
            
        response = requests.post(
            'https://www.strava.com/oauth/token',
            data={
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret'],
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
        )
        
        if response.status_code == 200:
            self._save_tokens(response.json())
            return True
        return False
    
    def get_activities(self, per_page=30, page=1):
        """Get a list of activities"""
        if not self.access_token and not self._refresh_token():
            return None
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(
            'https://www.strava.com/api/v3/athlete/activities',
            headers=headers,
            params={'per_page': per_page, 'page': page}
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:  # Unauthorized, token might be expired
            if self._refresh_token():
                return self.get_activities(per_page, page)
        return None
    
    def get_activity_streams(self, activity_id, stream_types=['latlng', 'time', 'altitude']):
        """Get activity streams (GPS data)"""
        if not self.access_token and not self._refresh_token():
            return None
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(
            f'https://www.strava.com/api/v3/activities/{activity_id}/streams',
            headers=headers,
            params={'keys': ','.join(stream_types), 'key_by_type': 'true'}
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:  # Unauthorized, token might be expired
            if self._refresh_token():
                return self.get_activity_streams(activity_id, stream_types)
        return None
    
    def download_original_activity(self, activity_id):
        """Download original activity file if available"""
        if not self.access_token and not self._refresh_token():
            return None
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(
            f'https://www.strava.com/api/v3/activities/{activity_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            activity = response.json()
            if 'external_id' in activity and activity['external_id']:
                try:
                    original_url = activity['external_id']
                    file_response = requests.get(original_url)
                    if file_response.status_code == 200:
                        return file_response.content
                except:
                    pass
        return None

strava = StravaAPI()

def load_polylines():
    """Load existing polylines from archive file"""
    if os.path.exists(POLYLINES_FILE):
        with open(POLYLINES_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_polylines(polylines):
    """Save polylines to archive file"""
    with open(POLYLINES_FILE, 'w') as f:
        json.dump(polylines, f, indent=2)

def update_polyline_archive(activity):
    """Update the polyline archive with a new activity"""
    polylines = load_polylines()
    if 'map' in activity and activity['map'] and activity['map']['summary_polyline']:
        polylines[str(activity['id'])] = {
            'summary_polyline': activity['map']['summary_polyline'],
            'name': activity.get('name', ''),
            'type': activity.get('type', ''),
            'start_date': activity.get('start_date', ''),
            'distance': activity.get('distance', 0)
        }
        save_polylines(polylines)


def streams_to_gpx(streams, activity_name, activity_date):
    """Convert Strava streams data to GPX format"""
    if not streams or 'latlng' not in streams or 'time' not in streams:
        return None
    
    gpx_template = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Strava API" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>{name}</name>
    <trkseg>
{trkpts}
    </trkseg>
  </trk>
</gpx>"""
    
    trkpts = []
    for i in range(len(streams['time']['data'])):
        lat, lng = streams['latlng']['data'][i]
        time = parser.parse(activity_date)
        time = time+ datetime.timedelta(seconds=int(streams['time']['data'][i]))
        ele = streams['altitude']['data'][i] if 'altitude' in streams else 0
        trkpts.append(f'      <trkpt lat="{lat}" lon="{lng}"><ele>{ele}</ele><time>{time.strftime("%Y-%m-%dT%H:%M:%SZ")}</time></trkpt>')
    
    return gpx_template.format(name=activity_name.encode("utf-8"), trkpts='\n'.join(trkpts))

def formattime(time):
    return str(timedelta(seconds=int(time)))
    
def get_pagination_params():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', DEFAULT_PER_PAGE))
    per_page = min(per_page, MAX_PER_PAGE)  # Enforce maximum
    return page, per_page

@app.route('/')
def index():
    if not strava.access_token and not strava._refresh_token():
        return redirect(url_for('login'))
    
    page, per_page = get_pagination_params()
    
    activities = strava.get_activities(per_page=per_page, page=page)
    if activities is None:
        return redirect(url_for('login'))
    
    # Check which activities already have downloaded files
    for activity in activities:
        # Update polyline archive for each activity we access
        update_polyline_archive(activity)
        activity['downloaded'] = os.path.exists(
            os.path.join(ACTIVITIES_DIR, f"{activity['id']}.gpx")
        ) or os.path.exists(
            os.path.join(ACTIVITIES_DIR, f"{activity['id']}.fit")
        )

    
    # Prepare pagination URLs
    base_params = {'per_page': per_page}
    
    prev_url = None
    if page > 1:
        prev_params = base_params.copy()
        prev_params['page'] = page - 1
        prev_url = url_for('index', **prev_params)
    
    next_params = base_params.copy()
    next_params['page'] = page + 1
    next_url = url_for('index', **next_params)
    
    per_page_options = [10, 20, 50, 100]
    
    return render_template(
        'index.html',
        activities=activities,
        current_page=page,
        per_page=per_page,
        prev_url=prev_url,
        next_url=next_url,
        per_page_options=per_page_options,
        formattime = formattime,
        download_all_url=url_for('download_all', page=page, per_page=per_page)
    )
	
@app.route('/heatmap/<z>_<x>_<y>')
def get_heatmap(z,x,y):
    return send_file(f'tiles\\{z}_{x}_{y}.png', mimetype='image/gif')
	
@app.route('/download_all')
def download_all():
    if not strava.access_token and not strava._refresh_token():
        return redirect(url_for('login'))
    
    page, per_page = get_pagination_params()
    activities = strava.get_activities(per_page=per_page, page=page)
    
    if not activities:
        return "No activities found", 404
    
    downloaded = []
    failed = []
    
    for activity in activities:
        # Update polyline archive for each activity
        update_polyline_archive(activity)
        activity_id = str(activity['id'])
        activity_name = activity.get('name', f'activity_{activity_id}').replace('/', '-')
        filename = f"{activity_id}.gpx"
        filepath = os.path.join(ACTIVITIES_DIR, filename)
        
        # Skip if already downloaded
        if os.path.exists(filepath) or os.path.exists(os.path.join(ACTIVITIES_DIR, f"{activity_id}.fit")):
            downloaded.append(activity_name)
            continue
        
        # Try to get the original file first
        original_data = strava.download_original_activity(activity_id)
        if original_data:
            ext = 'fit' if original_data.startswith(b'\x0e&\xb5\x02\x00') else 'gpx'
            filename = f"{activity_id}.{ext}"
            filepath = os.path.join(ACTIVITIES_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(original_data)
            downloaded.append(activity_name)
            continue
        
        # If no original file, try to get streams and convert to GPX
        streams = strava.get_activity_streams(activity_id)
        activity_date = activity['start_date_local']
        print(activity_name)
        if streams:
            gpx_data = streams_to_gpx(streams, activity_name, activity_date)
            if gpx_data:
                with open(filepath, 'w') as f:
                    f.write(gpx_data)
                downloaded.append(activity_name)
                continue
        
        failed.append(activity_name)
    
    # Return to the index page with a status message
    session['download_status'] = {
        'downloaded': downloaded,
        'failed': failed,
        'page': page,
        'per_page': per_page
    }
    return redirect(url_for('index', page=page, per_page=per_page))


@app.route('/login')
def login():
    if strava.access_token and strava._refresh_token():
        return redirect(url_for('index'))
    
    auth_url = (f"https://www.strava.com/oauth/authorize?client_id={strava.config['client_id']}"
                f"&response_type=code&redirect_uri={strava.config['redirect_uri']}"
                "&approval_prompt=force&scope=activity:read_all")
    return redirect(auth_url)

@app.route('/authorized')
def authorized():
    code = request.args.get('code')
    if not code:
        return "Authorization failed: no code received", 400
    
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': strava.config['client_id'],
            'client_secret': strava.config['client_secret'],
            'code': code,
            'grant_type': 'authorization_code'
        }
    )
    
    if response.status_code == 200:
        strava._save_tokens(response.json())
        return redirect(url_for('index'))
    else:
        return f"Authorization failed: {response.text}", 400

@app.route('/polylines')
def get_polylines():
    """Endpoint to view the polyline archive"""
    if not strava.access_token and not strava._refresh_token():
        return redirect(url_for('login'))
    
    polylines = load_polylines()
    return jsonify(polylines)

@app.route('/polylines/download')
def download_polylines():
    """Endpoint to download the polyline archive"""
    if not strava.access_token and not strava._refresh_token():
        return redirect(url_for('login'))
    
    return send_from_directory(ACTIVITIES_DIR, 'activity_polylines.json', as_attachment=True)
    
@app.route('/download/<activity_id>')
def download_activity(activity_id):
    if not strava.access_token and not strava._refresh_token():
        return redirect(url_for('login'))
    
    activity = next((a for a in strava.get_activities(per_page=90) if str(a['id']) == activity_id), None)
    if not activity:
        return "Activity not found", 404
    
    # Update polyline archive before processing download
    update_polyline_archive(activity)
    
    activity_name = activity.get('name', f'activity_{activity_id}').replace('/', '-')
    filename = f"{activity_id}.gpx"
    filepath = os.path.join(ACTIVITIES_DIR, filename)
    
    # Try to get the original file first
    original_data = strava.download_original_activity(activity_id)
    if original_data:
        # Determine file extension from content or activity type
        ext = 'fit' if original_data.startswith(b'\x0e&\xb5\x02\x00') else 'gpx'
        filename = f"{activity_id}.{ext}"
        filepath = os.path.join(ACTIVITIES_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(original_data)
        return redirect(url_for('download_file', filename=filename))
    
    # If no original file, try to get streams and convert to GPX
    streams = strava.get_activity_streams(activity_id)
    activity_date = activity['start_date_local']
    if streams:
        gpx_data = streams_to_gpx(streams, activity_name, activity_date)
        if gpx_data:
            with open(filepath, 'w') as f:
                f.write(gpx_data)
            return redirect(url_for('download_file', filename=filename))
    
    return "Failed to download activity", 400

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(ACTIVITIES_DIR, filename, as_attachment=True)

@app.route('/logout')
def logout():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    strava.access_token = None
    strava.refresh_token = None
    strava.token_expires_at = None
    return redirect(url_for('index'))

# Update the HTML template
if not os.path.exists('templates'):
    os.makedirs('templates')

with open('templates/index.html', 'w') as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Strava Activity Downloader</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #fc4c02; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        tr:hover { background-color: #f5f5f5; }
        .btn { 
            background-color: #fc4c02; color: white; padding: 6px 12px; 
            text-decoration: none; border-radius: 4px; display: inline-block;
            margin: 2px;
        }
        .btn:hover { background-color: #e03e00; }
        .btn-secondary {
            background-color: #6c757d;
        }
        .btn-secondary:hover {
            background-color: #5a6268;
        }
        .downloaded { color: #4CAF50; }
        .pagination { margin: 20px 0; display: flex; justify-content: space-between; }
        .per-page-selector { margin: 10px 0; }
        .status-message { 
            padding: 10px; margin: 10px 0; border-radius: 4px; 
            background-color: #f8f9fa; border: 1px solid #ddd;
        }
        .success { color: #155724; background-color: #d4edda; border-color: #c3e6cb; }
        .error { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }
        .archive-actions {
            margin: 20px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>Strava Activity Downloader</h1>
    {% if not activities %}
        <p>No activities found or not authenticated.</p>
        <a href="{{ url_for('login') }}" class="btn">Login with Strava</a>
    {% else %}
        {% if 'download_status' in session %}
            <div class="status-message {% if download_status.failed %}error{% else %}success{% endif %}">
                <p>Download results:</p>
                <ul>
                    {% for item in download_status.downloaded %}
                        <li>Downloaded: {{ item }}</li>
                    {% endfor %}
                    {% for item in download_status.failed %}
                        <li>Failed to download: {{ item }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% set _ = session.pop('download_status', None) %}
        {% endif %}

        <div class="per-page-selector">
            <form method="get" action="{{ url_for('index') }}">
                <label for="per_page">Activities per page:</label>
                <select name="per_page" id="per_page" onchange="this.form.submit()">
                    {% for option in per_page_options %}
                        <option value="{{ option }}" {% if option == per_page %}selected{% endif %}>{{ option }}</option>
                    {% endfor %}
                </select>
                <input type="hidden" name="page" value="{{ current_page }}">
            </form>
        </div>

        <table>
            <tr>
                <th>Date</th>
                <th>Name</th>
                <th>Type</th>
                <th>Distance</th>
                <th>Time</th>
                <th>Elevation gain</th>
                <th>Action</th>
            </tr>
            {% for activity in activities %}
            <tr>
                <td>{{ activity.start_date_local.split('T')[0] }}</td>
                <td><a href='https://www.strava.com/activities/{{activity.id}}'>{{ activity.name or 'Untitled' }}</a></td>
                <td>{{ activity.sport_type }}</td>
                <td>{{ "%.2f km"|format(activity.distance/1000) }}</td>
                <td>{{ formattime(activity.elapsed_time) }}</td>
                <td>{{ activity.total_elevation_gain }}</td>
                <td>
                    {% if activity.downloaded %}
                        <span class="downloaded">Downloaded</span>
                    {% else %}
                        <a href="{{ url_for('download_activity', activity_id=activity.id) }}" class="btn">Download</a>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>

        <div class="pagination">
            <div>
                {% if prev_url %}
                    <a href="{{ prev_url }}" class="btn btn-secondary">&laquo; Previous</a>
                {% endif %}
            </div>
            <div>
                Page {{ current_page }}
            </div>
            <div>
                {% if activities|length == per_page %}
                    <a href="{{ next_url }}" class="btn btn-secondary">Next &raquo;</a>
                {% endif %}
            </div>
        </div>

        <div>
            <a href="{{ download_all_url }}" class="btn">Download All on This Page</a>
            <a href="{{ url_for('logout') }}" class="btn btn-secondary">Logout</a>
        </div>
        
        <div class="archive-actions">
            <h3>Polyline Archive</h3>
            <p>Summary polylines for all accessed activities are saved in a JSON archive.</p>
            <a href="{{ url_for('get_polylines') }}" class="btn" target="_blank">View Archive</a>
            <a href="{{ url_for('download_polylines') }}" class="btn">Download Archive</a>
        </div>
    {% endif %}
</body>
</html>""")

if __name__ == '__main__':
    app.run(debug=True)