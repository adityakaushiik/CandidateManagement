# Candidate Management API

A comprehensive REST API for managing candidates and skills with MongoDB integration, resume parsing, and advanced filtering capabilities.

## Features

- ✅ **Complete CRUD operations** for Candidates and Skills
- ✅ **MongoDB** as the database with proper indexing
- ✅ **Pydantic models** with comprehensive validation
- ✅ **Proper separation of concerns** (Models, Repositories, Routes, Config)
- ✅ **Advanced filtering and pagination**
- ✅ **Resume parsing** with NLP (existing feature)
- ✅ **Async/await** for better performance
- ✅ **RESTful API design** with proper status codes
- ✅ **CORS enabled** for cross-origin requests

## Project Structure

```
CandidateManagement/
├── config/
│   └── database.py              # Database configuration and connection
├── models/
│   ├── candidate_model.py       # Candidate Pydantic models
│   └── skill_model.py           # Skill Pydantic models
├── repositories/
│   ├── candidate_repository.py  # Candidate database operations
│   └── skill_repository.py      # Skill database operations
├── routes/
│   ├── candidate_route.py       # Candidate API endpoints
│   ├── skill_route.py           # Skill API endpoints
│   └── resume_route.py          # Resume parsing endpoints
├── services/
│   └── resume_parser.py         # Resume parsing service
├── dependencies/
│   └── repository_deps.py       # Dependency injection
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── test_api.http               # API testing file
```

## Installation

### Prerequisites

- Python 3.9+
- MongoDB 4.4+ (running locally or remote)
- spaCy English model

### Setup Steps

1. **Clone the repository**
   ```bash
   cd CandidateManagement
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Update MongoDB connection string if needed:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=candidate_management
   ```

6. **Run MongoDB** (if running locally)
   ```bash
   mongod
   ```

7. **Start the application**
   ```bash
   uvicorn main:app --reload
   ```

8. **Access the API**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### Candidates API (`/api/candidates`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create a new candidate |
| GET | `/` | Get all candidates (with pagination & filters) |
| GET | `/{id}` | Get candidate by ID |
| PUT | `/{id}` | Update candidate |
| DELETE | `/{id}` | Delete candidate |
| POST | `/{id}/skills/{skill_name}` | Add skill to candidate |
| DELETE | `/{id}/skills/{skill_name}` | Remove skill from candidate |
| POST | `/search/by-skills` | Search candidates by skills |

### Skills API (`/api/skills`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create a new skill |
| POST | `/bulk` | Bulk create skills |
| GET | `/` | Get all skills (with pagination & filters) |
| GET | `/{id}` | Get skill by ID |
| GET | `/names` | Get all skill names (for autocomplete) |
| GET | `/category/{category}` | Get skills by category |
| PUT | `/{id}` | Update skill |
| DELETE | `/{id}` | Delete skill |

### Resume API (`/api/resume`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/parse` | Parse resume file (PDF/DOCX/TXT) |

## Data Models

### Candidate Model

```json
{
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "2024-01-15T00:00:00",
  "phone_number": "+1234567890",
  "location": "New York, USA",
  "email": "user@example.com",
  "skills": ["Python", "JavaScript"],
  "degree": "Bachelor of Technology",
  "total_experience": 5.5,
  "links": {
    "linkedin": "https://linkedin.com/in/username",
    "github": "https://github.com/username",
    "portfolio": "https://portfolio.com"
  }
}
```

### Skill Model

```json
{
  "name": "Python",
  "category": "Programming Language",
  "description": "High-level programming language"
}
```

## Validation Rules

### Candidate
- **first_name/last_name**: 1-100 characters, auto-capitalized
- **email**: Valid email format (validated by Pydantic)
- **phone_number**: 10-20 characters with optional `+` prefix
- **total_experience**: 0-50 years
- **skills**: Array of strings, auto-trimmed and capitalized
- **links**: URLs auto-prefixed with `https://` if missing

### Skill
- **name**: 1-100 characters, unique, auto-capitalized
- **category**: 0-100 characters, auto-capitalized
- **description**: 0-500 characters

## Query Parameters

### Candidates
- `page`: Page number (default: 1)
- `page_size`: Items per page (1-100, default: 10)
- `skill`: Filter by skill (partial match)
- `location`: Filter by location (partial match)
- `min_experience`: Minimum years of experience
- `sort_by`: Field to sort by (default: `created_at`)
- `sort_order`: `asc` or `desc` (default: `desc`)

### Skills
- `page`: Page number (default: 1)
- `page_size`: Items per page (1-100, default: 10)
- `category`: Filter by category (partial match)
- `search`: Search by skill name (partial match)
- `sort_by`: Field to sort by (default: `name`)
- `sort_order`: `asc` or `desc` (default: `asc`)

## Example Usage

### Create a Candidate
```bash
curl -X POST "http://localhost:8000/api/candidates/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "+1234567890",
    "skills": ["Python", "JavaScript"],
    "total_experience": 5.5
  }'
```

### Get Candidates with Filters
```bash
curl "http://localhost:8000/api/candidates/?skill=Python&min_experience=3&page=1&page_size=10"
```

### Create Skills in Bulk
```bash
curl -X POST "http://localhost:8000/api/skills/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {"name": "Python", "category": "Programming Language"},
    {"name": "React", "category": "Frontend Framework"}
  ]'
```

## Database Indexes

The application automatically creates the following indexes for optimal performance:

### Candidates Collection
- `email` (unique)
- `phone_number`
- `skills`
- `created_at`

### Skills Collection
- `name` (unique)
- `category`
- `created_at`

## Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `201`: Created
- `204`: No Content (successful deletion)
- `400`: Bad Request (validation error)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include descriptive messages:
```json
{
  "detail": "Candidate with this email already exists"
}
```

## Best Practices Implemented

1. **Separation of Concerns**: Models, Repositories, Routes, and Config are separated
2. **Dependency Injection**: Using FastAPI's dependency system
3. **Async/Await**: All database operations are asynchronous
4. **Validation**: Comprehensive Pydantic models with custom validators
5. **Indexing**: Database indexes for frequently queried fields
6. **Error Handling**: Proper HTTP status codes and error messages
7. **Documentation**: Auto-generated API docs with FastAPI
8. **Type Hints**: Full type annotations for better IDE support
9. **Pagination**: All list endpoints support pagination
10. **Filtering**: Advanced filtering capabilities

## Testing

Use the `test_api.http` file with REST Client extension in VS Code or JetBrains IDEs to test all endpoints.

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License

