# AI Coach - Real-time Posture Analysis

![Django](https://img.shields.io/badge/Django-6.0-green) ![DRF](https://img.shields.io/badge/DRF-3.14-blue) ![JWT](https://img.shields.io/badge/JWT-Auth-orange) ![WebSocket](https://img.shields.io/badge/WebSocket-Channels-purple)

A comprehensive Django-based web application for real-time AI-powered posture analysis and presentation coaching using computer vision.

## 🎯 Features

### Core Functionality
- **Real-time Pose Detection** - Uses MediaPipe for accurate body pose tracking via webcam
- **Live AI Feedback** - WebSocket-based real-time feedback system for posture guidance
- **Session Recording** - Automatically records and analyzes training sessions
- **Performance Scoring** - Intelligent algorithm calculates performance metrics including:
  - Hand crossing detection
  - Eye contact analysis
  - Movement smoothness
  - Symmetry assessment
  - Jerk detection

### Security
- **JWT Authentication** - Secure token-based authentication with HttpOnly cookies
- **CSRF Protection** - Built-in Django CSRF middleware
- **Role-based Access Control** - Session ownership validation on backend
- **Secure Cookies** - HttpOnly, SameSite, and Secure flags
- **Token Refresh** - Automatic token rotation every 10 minutes
- **XSS Protection** - Template auto-escaping and HttpOnly enforcement

### User Features
- **Session History** - View all past training sessions with detailed statistics
- **Performance Reports** - Detailed analysis of each training session
- **User Dashboard** - Overview of all sessions and statistics
- **User Authentication** - Secure login/registration system

## 🏗️ Tech Stack

### Backend
- **Django** 6.0+ - Web framework
- **Django REST Framework** 3.14+ - RESTful API
- **django-rest-framework-simplejwt** 5.3+ - JWT authentication
- **Django Channels** 4.0+ - WebSocket support
- **Daphne** 4.0+ - ASGI server

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling with variables and responsive design
- **Vanilla JavaScript** - Client-side logic
- **MediaPipe** - Pose detection library

### Database
- **SQLite** - Development (default)
- **PostgreSQL** - Production (optional)

### Deployment
- **WhiteNoise** - Static file serving
- **Python 3.8+** - Runtime

## 🔒 Security Features

### Authentication & Authorization
```python
✅ JWT tokens stored in HttpOnly cookies
✅ Automatic token refresh every 10 minutes
✅ LoginRequiredMixin on protected views
✅ Session ownership validation
✅ CSRF token protection
```

### Endpoints Protection
| Endpoint | Auth Required | Scope |
|----------|---------------|-------|
| `/login/` | ❌ No | Public |
| `/register/` | ❌ No | Public |
| `/dashboard/` | ✅ Yes | Own sessions only |
| `/coach/` | ✅ Yes | Authenticated users |
| `/session/<uuid>/` | ✅ Yes | Own sessions only |
| `/api/sessions/` | ✅ Yes | Own sessions only |

### Cookie Configuration
```javascript
// HttpOnly Cookies - Not accessible to JavaScript
access_token:
  - HttpOnly: ✅
  - Secure: ✅ (production only)
  - SameSite: Lax
  - Max-Age: 15 minutes

refresh_token:
  - HttpOnly: ✅
  - Secure: ✅ (production only)
  - SameSite: Lax
  - Max-Age: 7 days
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git
- PostgreSQL 12+ (optional, for production)

### Development Setup

#### 1. Clone Repository
```bash
git clone 
cd django-ai-coach
cd Django-AI-Coach-presentation
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Database Setup
```bash
# Apply migrations
python manage.py migrate

# Create superuser (optional, for future admin panel (not support in this version))
python manage.py createsuperuser

# Create test user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('testuser1', 'test@example.com', 'testpass123')
>>> exit()
```

#### 5. Run Development Server
```bash
# Using Daphne (ASGI)
python manage.py runserver

# Server runs at http://127.0.0.1:8000/
```

## 🚀 Usage

### 1. Create Account
1. Navigate to `http://localhost:8000/register/`
2. Enter username and password
3. Click "Register"
4. Go to login page and sign in

### 2. Access Dashboard
1. After login, you'll be redirected to dashboard
2. View your past training sessions
3. Click on any session to see detailed performance report

### 3. Start Training Session
1. Click "AI Coach" in navigation
2. Grant camera permissions when prompted
3. Position yourself in front of the camera
4. Click "Start" to begin session
5. Receive real-time feedback on posture
6. Click "Stop" when done
7. View your session report

### 4. View Session Reports
1. From dashboard, click on any session
2. View detailed metrics:
   - Overall score (0-100%)
   - Session duration
3. In future:
   - Hand crossing count
   - Eye contact percentage
   - Movement smoothness
   - Symmetry score
   - Jerk analysis

## 🔌 API Documentation

### Authentication Endpoints

#### Login
```http
POST /api/token/
Content-Type: application/json

{
  "username": "testuser1",
  "password": "testpass123"
}

Response: 200 OK
Set-Cookie: access_token=...; HttpOnly
Set-Cookie: refresh_token=...; HttpOnly
```

#### Verify Auth
```http
GET /api/auth/verify/
Cookie: access_token=...

Response: 200 OK
{
  "authenticated": true,
  "user": "testuser1",
  "user_id": 1
}
```

#### Logout
```http
POST /api/auth/logout/
Cookie: access_token=...

Response: 200 OK
Set-Cookie: access_token=; max_age=0
Set-Cookie: refresh_token=; max_age=0
```

### Session Endpoints

#### List Sessions
```http
GET /api/sessions/
Cookie: access_token=...

Response: 200 OK
{
  "count": 5,
  "results": [
    {
      "uuid": "abc-123",
      "start_time": "2024-05-15T14:00:00Z",
      "end_time": "2024-05-15T14:10:00Z",
      "score": 85.5,
      "created_at": "2024-05-15T14:10:05Z"
    }
  ]
}
```

#### Get Session Details
```http
GET /api/sessions/{uuid}/
Cookie: access_token=...

Response: 200 OK
{
  "uuid": "abc-123",
  "start_time": "2024-05-15T14:00:00Z",
  "end_time": "2024-05-15T14:10:00Z",
  "score": 85.5
}
```

#### Delete Session
```http
DELETE /api/sessions/{uuid}/
Cookie: access_token=...

Response: 204 No Content
```

### WebSocket Endpoint

#### Connect to Coach
```javascript
// JavaScript
const ws = new WebSocket('ws://localhost:8000/ws/coach/');

ws.onopen = () => {
  console.log('Connected to AI Coach');
};

// Send pose data
ws.send(JSON.stringify({
  landmarks: [...],
  hands_crossed: 0,
  eye_contact: 0.95,
  movement: 0.5
}));

// Receive feedback
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'live_update') {
    console.log('Score:', data.score);
  }
};
```

## 🏛️ Architecture

### Project Structure
```
Django-AI-Coach-presentation/
├── analyzer/                    # Main app
│   ├── models.py               # Database models (Session)
│   ├── views.py                # Django views + API endpoints
│   ├── consumers.py            # WebSocket consumer
│   ├── routing.py              # WebSocket routing
│   ├── authentication.py       # JWT authentication
│   ├── middleware.py           # Custom middleware
│   ├── scoring.py              # Performance scoring algorithm
│   └── tests.py                # Unit tests
│
├── api/                         # API app
│   ├── urls.py                 # API routes
│   └── tests.py
│
├── templates/                   # HTML templates
│   ├── base.html              # Base template
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # Session history
│   ├── coach.html             # Training interface
│   └── session_report.html    # Session details
│
├── static/                      # Static files
│   ├── css/styles.css         # Global styles
│   ├── js/
│   │   ├── auth.js            # Authentication manager
│   │   ├── cv.js              # AI Coach logic
│   │   └── utils.js           # Utilities
│   └── img/
│
├── Django_AI_Coach_presentation/
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL routing
│   ├── asgi.py                # ASGI configuration
│   └── wsgi.py                # WSGI configuration
│
├── manage.py                    # Django CLI
├── requirements.txt             # Python dependencies
└── db.sqlite3                   # SQLite database (dev)
```

### Data Flow

#### Authentication Flow
```
User Login → /api/token/ → JWT Token Generated
            ↓
        HttpOnly Cookie Set
            ↓
    JWTCookieAuthMiddleware → request.user populated
            ↓
    LoginRequiredMixin → Access Granted
```

#### Training Session Flow
```
User clicks "Start" → WebSocket Connection
                    ↓
    Browser → MediaPipe Pose Detection
                    ↓
    Pose Data → /ws/coach/ (WebSocket)
                    ↓
    CoachConsumer → Scoring Algorithm
                    ↓
    Live Feedback → Browser (JSON)
                    ↓
    User completes → /api/sessions/ (Save)
```

## 🧪 Testing

### Manual Testing

#### Test Login
```bash
# 1. Open browser: http://localhost:8000/login/
# 2. Enter credentials:
#    Username: testuser1
#    Password: testpass123
# 3. Expected: Redirect to /dashboard/ (no flashing to security check (refresh))
```

#### Test Dashboard
```bash
# 1. After login, navigate to /dashboard/
# 2. Expected:
#    - Sessions list displays
#    - Auto-refresh works every 10 minutes
#    - No console errors
```

#### Test Coach
```bash
# 1. Click "AI Coach" in navigation
# 2. Expected:
#    - Camera stream displays
#    - WebSocket connects
#    - Real-time feedback shows
#    - Start/Stop buttons work
```

#### Test Security
```bash
# 1. Open DevTools (F12)
# 2. Application → Cookies
# 3. Expected:
#    - access_token (HttpOnly: ✅)
#    - refresh_token (HttpOnly: ✅)
#    - document.cookie shows nothing
```

## 📊 Performance Scoring

The AI Coach uses a smart algorithm to evaluate posture quality:

### Metrics
- **Hand Crossing** - Detected when hands cross over chest center
- **Eye Contact** - Measured using facial landmarks
- **Movement Smoothness** - Calculated using velocity variance
- **Symmetry** - Compared left vs right body halves
- **Jerk Detection** - Identified rapid acceleration changes

### Score Calculation
```
Final Score = Weighted Average of:
  - Hand Position (20%)
  - Eye Contact (20%)
  - Movement Smoothness (20%)
  - Symmetry (20%)
  - Jerk Analysis (20%)

Result: 0-100% (100% = Perfect posture)
```

## 🌐 Deployment

### Prerequisites
- Ubuntu Server 20.04+
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Gunicorn

### Production Setup

#### 1. Clone and Setup
```bash
git clone
cd django-ai-coach/Django-AI-Coach-presentation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Update Settings
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ai_coach_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

#### 3. Migrations & Static Files
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

#### 4. Gunicorn
```bash
# Install
pip install gunicorn

# Run
gunicorn --workers 4 --bind 0.0.0.0:8000 \
  Django_AI_Coach_presentation.wsgi:application
```

#### 5. Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /static/ {
        alias /path/to/static/;
    }
}
```

## 🆘 Troubleshooting

### Issue: Camera Permission Denied
**Solution**: 
- Check browser permissions for camera access
- Try different browser (Chrome recommended)
- Ensure HTTPS in production

### Issue: WebSocket Connection Failed
**Solution**:
- Verify Daphne is running (not Django dev server)
- Check firewall settings for WebSocket port
- Review browser console for errors

### Issue: Tokens Not Working
**Solution**:
- Clear browser cookies
- Check HttpOnly cookie settings
- Verify JWT secret key in settings

### Issue: Performance Issues
**Solution**:
- Reduce MediaPipe model complexity
- Increase Gunicorn workers
- Enable database connection pooling
- Use CDN for static files
