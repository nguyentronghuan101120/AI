# AI Project

A FastAPI-based AI application that provides chat and image processing capabilities with streaming support.

## Features

- Real-time chat streaming with AI
- Image processing capabilities
- Web data services
- Tool-based AI interactions
- CORS-enabled API endpoints
- Static file serving for outputs

## Project Structure

```
src/
├── constants/         # System prompts and configuration
├── data/             # Data storage
├── domain/           # Domain models
├── models/           # Request/Response models
├── routes/           # API route definitions
├── services/         # Business logic
├── utils/            # Utility functions
└── main.py          # Application entry point
```

## API Endpoints

### Chat API
- `POST /api/v1/chat/stream`: Stream chat responses in real-time
  - Supports tool-based interactions
  - Returns streaming responses in text/event-stream format

## Getting Started

### Prerequisites
- Python 3.x
- FastAPI
- Uvicorn

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the server using:
```bash
uvicorn main:app --reload --port 8080
```

The application will be available at `http://localhost:8080`

## Error Handling

The application includes comprehensive error handling for:
- Custom exceptions
- Validation errors
- Global exceptions

All errors return standardized JSON responses with appropriate status codes.

## Static Files

The application serves static files from the `/outputs` directory, mounted at the `/outputs` endpoint.

## Development

The project uses a modular architecture with clear separation of concerns:
- Routes handle HTTP requests and responses
- Services contain business logic
- Models define data structures
- Utils provide helper functions

## License

[Add your license information here]
