# S4C Trajectory API Services

![S4C Trajectory API Services](https://56fwnhyzti.ufs.sh/f/aK4w8mNL3AiP2bx5PeEL4ocBZQyGd7xSpqsOt8wHiMNljnz1)

A comprehensive API service for managing and analyzing trajectory data with a modern web interface.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🔍 Overview

S4C Trajectory API Services is a full-stack application designed to handle trajectory data processing, storage, and visualization. The system provides RESTful APIs for trajectory management and a user-friendly frontend interface for data interaction.

## ✨ Features

- **RESTful API**: Comprehensive API endpoints for trajectory data management
- **Data Processing**: Efficient trajectory data processing and analysis
- **Web Interface**: Modern frontend for data visualization and interaction
- **Containerized Deployment**: Docker-based deployment for easy setup and scalability
- **Data Storage**: Robust data storage and retrieval mechanisms

## 🏗 Architecture

The application follows a microservices architecture with the following components:

- **Backend**: Python-based API service (94.6% of codebase)
- **Frontend**: Streamlit-based web interface for interactive data visualization
- **Data Layer**: Structured data storage and management
- **Containerization**: Docker and Docker Compose for orchestration

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- Docker (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)
- Git

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Jaylaelike/s4c-trajectory-api-services.git
cd s4c-trajectory-api-services
```

### 2. Build and Run with Docker Compose

```bash
docker-compose up --build
```

This command will:
- Build the backend and frontend services
- Set up the necessary containers
- Start all services

### 3. Access the Application

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 💻 Usage

### Starting the Services

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
```

### Stopping the Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 📚 API Documentation

### Base URL

```
http://localhost:8000/api
```

### Common Endpoints

#### Trajectory Management

- `GET /trajectories` - List all trajectories
- `POST /trajectories` - Create a new trajectory
- `GET /trajectories/{id}` - Get trajectory by ID
- `PUT /trajectories/{id}` - Update trajectory
- `DELETE /trajectories/{id}` - Delete trajectory

#### Data Analysis

- `POST /analyze` - Analyze trajectory data
- `GET /statistics` - Get trajectory statistics

For detailed API documentation, visit http://localhost:8000/docs when the service is running.

## 📁 Project Structure

```
s4c-trajectory-api-services/
├── backend/              # Python backend service
│   ├── app/             # Application code
│   ├── tests/           # Backend tests
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend container definition
│
├── frontend/            # Streamlit frontend application
│   ├── app.py          # Main Streamlit app
│   ├── pages/          # Multi-page app structure
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile      # Frontend container definition
│
├── data/               # Data storage directory
│   └── samples/        # Sample data files
│
├── docker-compose.yml  # Service orchestration
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Backend Configuration
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./data/trajectories.db

# Frontend Configuration
FRONTEND_PORT=8501
STREAMLIT_SERVER_PORT=8501
API_BASE_URL=http://localhost:8000

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

### Backend Configuration

Backend-specific settings can be configured in `backend/config.py` or through environment variables.

### Frontend Configuration

Frontend configuration can be modified in `frontend/.streamlit/config.toml` or through Streamlit environment variables.

## 🛠 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit development server
streamlit run app.py
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (if available)
cd frontend
pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Write unit tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Jaylaelike** - [GitHub Profile](https://github.com/Jaylaelike)

## 🐛 Issues

If you encounter any issues or have suggestions, please file an issue on the [GitHub Issues](https://github.com/Jaylaelike/s4c-trajectory-api-services/issues) page.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the maintainers

## 🙏 Acknowledgments

- Thanks to all contributors who have helped with this project
- Built with modern web technologies and best practices

---

**Note**: This project is under active development. Features and documentation may change.