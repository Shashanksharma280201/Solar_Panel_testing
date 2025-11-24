# Solar Panel Defect Detection - Deployment Guide

A web application for AI-powered solar panel defect detection using Electroluminescence (EL) imaging.

## Project Structure

```
webapp/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .dockerignore         # Docker ignore file
├── .gitignore            # Git ignore file
├── DEPLOY.md             # This file
├── templates/
│   └── index.html        # Frontend UI
├── static/
│   └── images/
│       ├── original/     # Original grayscale images (100 images)
│       └── results/      # Annotated result images (100 images)
└── data/
    ├── detection_report.json      # Full detection data (2165 objects)
    └── summary_statistics.json    # Summary statistics
```

## Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Navigate to webapp folder
cd webapp

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at: **http://localhost:5000**

---

## Deployment Options

### Option 1: Docker Deployment

#### Build and Run Locally

```bash
# Build Docker image
docker build -t solar-defect-detection .

# Run container
docker run -p 5000:5000 solar-defect-detection

# Run in background
docker run -d -p 5000:5000 --name solar-app solar-defect-detection
```

Access at: **http://localhost:5000**

#### Docker Commands

```bash
# Stop container
docker stop solar-app

# Remove container
docker rm solar-app

# View logs
docker logs solar-app
```

---

### Option 2: Deploy to Render (Free)

1. **Create a GitHub Repository**
   ```bash
   cd webapp
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/solar-defect-detection.git
   git push -u origin main
   ```

2. **Create `render.yaml`** in the webapp folder:
   ```yaml
   services:
     - type: web
       name: solar-defect-detection
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn app:app --bind 0.0.0.0:$PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.0
   ```

3. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click "New" > "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the configuration
   - Click "Create Web Service"

---

### Option 3: Deploy to Railway (Free Tier)

1. **Push to GitHub** (same as above)

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" > "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and deploys

3. **Add `Procfile`** (create in webapp folder):
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT
   ```

---

### Option 4: Deploy to Heroku

1. **Install Heroku CLI**
   ```bash
   # Ubuntu/Debian
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Create `Procfile`**:
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT
   ```

3. **Create `runtime.txt`**:
   ```
   python-3.11.0
   ```

4. **Deploy**
   ```bash
   heroku login
   heroku create solar-defect-detection
   git push heroku main
   heroku open
   ```

---

### Option 5: Deploy to Google Cloud Run

1. **Install Google Cloud SDK**

2. **Build and Deploy**
   ```bash
   # Authenticate
   gcloud auth login

   # Set project
   gcloud config set project YOUR_PROJECT_ID

   # Build and deploy
   gcloud run deploy solar-defect-detection \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

---

### Option 6: Deploy to AWS (Elastic Beanstalk)

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize and Deploy**
   ```bash
   eb init -p python-3.11 solar-defect-detection
   eb create solar-defect-env
   eb open
   ```

---

### Option 7: Deploy to DigitalOcean App Platform

1. **Push to GitHub**

2. **Create App on DigitalOcean**
   - Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
   - Click "Apps" > "Create App"
   - Connect GitHub repository
   - Configure:
     - Run Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
     - HTTP Port: 5000

---

### Option 8: Deploy to VPS (Ubuntu Server)

```bash
# SSH into your server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv nginx -y

# Clone your repository
git clone https://github.com/YOUR_USERNAME/solar-defect-detection.git
cd solar-defect-detection/webapp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install gunicorn
pip install gunicorn

# Test the app
gunicorn app:app --bind 0.0.0.0:5000

# Create systemd service
sudo nano /etc/systemd/system/solar-app.service
```

**systemd service file (`/etc/systemd/system/solar-app.service`):**
```ini
[Unit]
Description=Solar Panel Defect Detection App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/webapp
Environment="PATH=/path/to/webapp/venv/bin"
ExecStart=/path/to/webapp/venv/bin/gunicorn app:app --bind 0.0.0.0:5000 --workers 2

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable solar-app
sudo systemctl start solar-app

# Check status
sudo systemctl status solar-app
```

**Nginx configuration (`/etc/nginx/sites-available/solar-app`):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/webapp/static;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/solar-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `5000` |
| `FLASK_DEBUG` | Enable debug mode | `False` |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/images` | GET | List available images |
| `/api/summary` | GET | Get detection statistics |
| `/api/analyze` | POST | Analyze an image (simulated) |
| `/original/<filename>` | GET | Serve original image |
| `/results/<filename>` | GET | Serve result image |

---

## Data Information

- **Total Images**: 100 solar panel EL images
- **Total Detected Objects**: 2,165 defects
- **Detection Categories**:
  - Good Condition: 6 images
  - Needs Repair: 62 images
  - Critical: 27 images
  - Fully Damaged: 5 images

---

## Troubleshooting

### Port already in use
```bash
# Find process using port 5000
lsof -i :5000
# or
fuser 5000/tcp

# Kill the process
kill -9 <PID>
# or
fuser -k 5000/tcp
```

### Permission denied on images
```bash
chmod -R 755 static/images/
```

### Docker build fails
```bash
# Clean Docker cache
docker system prune -a
docker build --no-cache -t solar-defect-detection .
```

---

## Support

For issues and questions, check:
- Application logs: `docker logs solar-app`
- Flask logs: Check console output
- Nginx logs: `/var/log/nginx/error.log`
