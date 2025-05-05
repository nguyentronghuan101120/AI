# AI Project

A FastAPI-based AI application that provides chat and image processing capabilities with streaming support.

## Features

- Real-time chat streaming with AI
- Image processing and manipulation
- Web data services for external data retrieval
- File processing capabilities
- Tool-based AI interactions
- CORS-enabled API endpoints
- Static file serving for outputs

## Project Structure

```
src/
├── constants/         # System prompts and configuration
│   ├── system_prompts.py  # AI system prompts
│   └── file_type.py      # File type definitions
├── models/           # Request/Response models
│   ├── requests/     # Request models
│   └── responses/    # Response models
├── routes/           # API route definitions
│   ├── chat_routes.py
│   └── process_file_routes.py
├── services/         # Business logic
│   ├── chat_service.py
│   ├── image_service.py
│   ├── process_file_service.py
│   └── web_data_service.py
├── utils/            # Utility functions
│   ├── tools/        # Tool implementations
│   ├── client.py     # HTTP client utilities
│   ├── exception.py  # Custom exceptions
│   └── image_pipeline.py
└── main.py          # Application entry point
```

## API Endpoints

### Chat API

- `POST /api/v1/chat/stream`: Stream chat responses in real-time
  - Supports tool-based interactions
  - Returns streaming responses in text/event-stream format

### File Processing API

- `POST /api/v1/process-file`: Process and analyze files
  - Supports various file types
  - Returns processed results

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
