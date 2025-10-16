# Fuzzy Search Documentation

## Overview

The fuzzy search functionality allows you to search for users and candidates across multiple fields with tolerance for typos and partial matches. It searches through:
- First Name
- Last Name  
- Full Name (first_name + last_name combined)
- Email
- Phone Number

## Features

✅ **Multi-field Search**: Searches across first_name, last_name, email, and phone_number simultaneously
✅ **Full Name Search**: Intelligently combines first and last names for better matching
✅ **Partial Matching**: Find results even with incomplete search terms
✅ **Typo Tolerance**: Handles minor spelling variations
✅ **Relevance Scoring**: Results are ranked by relevance (exact matches first)
✅ **Pagination**: Supports paginated results
✅ **Additional Filters**: Combine search with role, location, or experience filters
✅ **Collection Agnostic**: Works with both "users" and "candidates" collections

## API Endpoints

### 1. Search Users

**Endpoint:** `GET /api/search/users`

**Query Parameters:**
- `q` (required): Search query string (min 1 character)
- `page` (optional): Page number (default: 1, min: 1)
- `page_size` (optional): Results per page (default: 20, min: 1, max: 100)
- `role_id` (optional): Filter by role ID (1=Admin, 2=Sub-Admin, 3=Candidate)

**Authentication:** Required (Admin or Sub-Admin)

**Example Requests:**
```http
# Search by name
GET /api/search/users?q=John

# Search by email
GET /api/search/users?q=john@example.com

# Search with role filter
GET /api/search/users?q=admin&role_id=1

# Search with pagination
GET /api/search/users?q=doe&page=2&page_size=10
```

**Response:**
```json
{
  "total": 15,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone_number": "+1234567890",
      "role_id": 3,
      "created_at": "2025-10-16T12:00:00Z",
      "updated_at": "2025-10-16T12:00:00Z"
    }
  ]
}
```

### 2. Search Candidates

**Endpoint:** `GET /api/search/candidates`

**Query Parameters:**
- `q` (required): Search query string (min 1 character)
- `page` (optional): Page number (default: 1, min: 1)
- `page_size` (optional): Results per page (default: 20, min: 1, max: 100)
- `location` (optional): Filter by location (case-insensitive)
- `min_experience` (optional): Minimum years of experience (min: 0)

**Authentication:** Required (Admin or Sub-Admin)

**Example Requests:**
```http
# Search by name
GET /api/search/candidates?q=Alice Smith

# Search with location filter
GET /api/search/candidates?q=developer&location=New York

# Search with experience filter
GET /api/search/candidates?q=python&min_experience=5

# Search with multiple filters
GET /api/search/candidates?q=engineer&location=SF&min_experience=3&page_size=50
```

**Response:**
```json
{
  "total": 8,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "first_name": "Alice",
      "last_name": "Smith",
      "email": "alice.smith@example.com",
      "phone_number": "+9876543210",
      "location": "New York",
      "skills": ["Python", "Django", "React"],
      "degree": "Computer Science",
      "total_experience": 5.5,
      "created_at": "2025-10-15T10:00:00Z",
      "updated_at": "2025-10-15T10:00:00Z"
    }
  ]
}
```

## Search Algorithm

### Relevance Scoring

Results are ranked by a scoring system:

1. **Exact Match**: +100 points
   - Exact match of search term with any field
   
2. **Exact Full Name Match**: +150 points
   - Search term exactly matches "first_name last_name"
   
3. **Starts With**: +50-75 points
   - Field value starts with the search term
   
4. **Contains**: +25-40 points
   - Field value contains the search term
   
5. **Word Start**: +15 points
   - Any word in the field starts with search term

### Fuzzy Matching

The search uses regex patterns to enable:
- **Case-insensitive matching**: "john" matches "John", "JOHN", "JoHn"
- **Partial matching**: "ali" matches "Alice", "Alison", "Natalie"
- **Multi-word matching**: "john doe" matches both words in any order
- **Special character tolerance**: Ignores special characters in search

## Usage Examples

### Example 1: Search by Full Name
```http
GET /api/search/candidates?q=John Doe
Authorization: Bearer YOUR_TOKEN
```
This will find candidates with:
- first_name="John" AND last_name="Doe"
- Any field containing "John" or "Doe"

### Example 2: Search by Partial Email
```http
GET /api/search/users?q=john.smith
Authorization: Bearer YOUR_TOKEN
```
Matches emails like:
- john.smith@example.com
- john.smith123@company.org

### Example 3: Search with Filters
```http
GET /api/search/candidates?q=developer&location=San Francisco&min_experience=3
Authorization: Bearer YOUR_TOKEN
```
Finds candidates who:
- Have "developer" in any searchable field
- AND are located in San Francisco
- AND have at least 3 years of experience

### Example 4: Phone Number Search
```http
GET /api/search/candidates?q=+1-555-123
Authorization: Bearer YOUR_TOKEN
```
Matches phone numbers containing these digits

## Integration Example (Frontend)

### JavaScript/TypeScript
```typescript
async function searchCandidates(query: string, page = 1) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(
    `http://localhost:8000/api/search/candidates?q=${encodeURIComponent(query)}&page=${page}&page_size=20`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  if (!response.ok) {
    throw new Error('Search failed');
  }
  
  return await response.json();
}

// Usage
const results = await searchCandidates('john doe');
console.log(`Found ${results.total} candidates`);
results.results.forEach(candidate => {
  console.log(`${candidate.first_name} ${candidate.last_name}`);
});
```

### Python
```python
import requests

def search_users(query: str, token: str, role_id: int = None):
    params = {
        'q': query,
        'page': 1,
        'page_size': 20
    }
    
    if role_id:
        params['role_id'] = role_id
    
    response = requests.get(
        'http://localhost:8000/api/search/users',
        params=params,
        headers={'Authorization': f'Bearer {token}'}
    )
    
    response.raise_for_status()
    return response.json()

# Usage
results = search_users('admin', token='YOUR_TOKEN', role_id=1)
print(f"Found {results['total']} admin users")
```

## Performance Tips

1. **Use Specific Terms**: More specific search terms return more relevant results
2. **Combine Filters**: Use location/experience/role filters to narrow results
3. **Pagination**: Use reasonable page sizes (20-50) for better performance
4. **Index Your Database**: Ensure MongoDB indexes are created on searchable fields

## Security

- All search endpoints require authentication
- Only Admin and Sub-Admin roles can access search functionality
- No sensitive data (passwords) are returned in search results
- Results are filtered based on user permissions

## Troubleshooting

### No Results Found
- Check spelling of search term
- Try shorter/partial search terms
- Verify the data exists in the collection
- Check filters aren't too restrictive

### Slow Performance
- Reduce page_size
- Add more specific filters
- Ensure database indexes are created
- Consider adding minimum search term length

### Authentication Errors
- Verify your JWT token is valid and not expired
- Ensure you have Admin or Sub-Admin role
- Check Authorization header format: `Bearer YOUR_TOKEN`

