# 🤖 Interview Bot - AI-Powered Interview Assistant

An intelligent interview bot powered by AI that conducts realistic job interviews with voice capabilities, built with FastAPI and React.

## 🚀 Features

- **AI-Powered Interviews**: Realistic interview questions based on job roles
- **Multiple Interview Types**: Meta Ads Expert, Software Engineer, Data Scientist, and more
- **Real-time Chat**: Interactive interview experience
- **Session Management**: Track interview progress and history
- **MongoDB Backend**: Scalable data storage
- **Modular Architecture**: Production-ready, enterprise-grade structure
- **Health Monitoring**: Comprehensive system health checks

## 🏗️ Architecture

```
interview-bot/
├── backend/                 # FastAPI backend
│   ├── app.py              # Main application entry point
│   ├── config/             # Configuration management
│   ├── models/             # Data models & schemas
│   ├── services/           # Business logic layer
│   ├── routes/             # API endpoints
│   ├── data/               # Static content & prompts
│   └── requirements.txt    # Python dependencies
└── frontend/               # React frontend
    ├── src/
    │   ├── components/     # React components
    │   └── App.tsx         # Main application
    └── package.json        # Node.js dependencies
```

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **MongoDB** (local or cloud)
- **OpenRouter API Key** (for AI responses)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd interview-bot
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the `backend/` directory:
```bash
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=interview_bot

# AI Service Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

#### Start MongoDB
```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt update
sudo apt install mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify MongoDB is running
mongosh --eval "db.runCommand('ping')"
```

#### Run the Backend Server
```bash
cd backend
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

### 3. Frontend Setup

#### Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### Run the Frontend Development Server
```bash
npm run dev
```

The frontend will be available at: `http://localhost:5173`

## 🎯 Quick Start Commands

### Complete Setup (One-liner)
```bash
# Backend
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Frontend (in new terminal)
cd frontend && npm install && npm run dev
```

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
Visit: `http://localhost:8000/docs`

## 📚 API Endpoints

### Session Management
- `POST /api/sessions/init` - Initialize new interview session
- `GET /api/sessions/{id}/history` - Get session history
- `GET /api/sessions/{id}/status` - Get session status
- `POST /api/sessions/start` - Start interview
- `POST /api/sessions/end` - End interview

### Chat
- `POST /api/chat/send` - Send message to AI interviewer

### System
- `GET /` - Root endpoint
- `GET /health` - Health check with system monitoring

## 🔧 Development Commands

### Backend Development
```bash
# Run with auto-reload
uvicorn app:app --reload

# Run on specific port
uvicorn app:app --port 8001

# Run with debug mode
uvicorn app:app --reload --log-level debug
```

### Frontend Development
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Database Commands
```bash
# Connect to MongoDB
mongosh

# Switch to interview_bot database
use interview_bot

# View sessions
db.sessions.find()

# View session count
db.sessions.countDocuments()
```

## 🧪 Testing

### Test API Endpoints
```bash
# Test health check
curl http://localhost:8000/health

# Test session creation
curl -X POST http://localhost:8000/api/sessions/init \
  -H "Content-Type: application/json" \
  -d '{"role_id": "meta-ads-expert"}'

# Test chat message
curl -X POST http://localhost:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your_session_id", "message": "Hello!"}'
```

## 🔍 Troubleshooting

### Common Issues

#### MongoDB Connection Error
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check MongoDB logs
sudo journalctl -u mongod
```

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Python Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Frontend Build Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📊 Monitoring

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "service": "Interview Bot API",
  "version": "1.0.0",
  "checks": {
    "database": "healthy",
    "ai_service": "configured",
    "memory": {
      "total_gb": 16.0,
      "available_gb": 8.5,
      "percent_used": 47.0
    }
  }
}
```

## 🚀 Production Deployment

### Environment Variables
```bash
# Production environment
MONGODB_URL=mongodb://your-production-mongodb-url
OPENROUTER_API_KEY=your-production-api-key
DATABASE_NAME=interview_bot_prod
```

### Docker Deployment (Future)
```bash
# Build and run with Docker
docker build -t interview-bot .
docker run -p 8000:8000 interview-bot
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [ARCHITECTURE.md](backend/ARCHITECTURE.md) for technical details
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join the community discussions

## 🎯 Roadmap

- [ ] Voice bot integration
- [ ] User authentication system
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant support
- [ ] Mobile app
- [ ] Real-time collaboration features

---

**Happy Interviewing! 🎉**
