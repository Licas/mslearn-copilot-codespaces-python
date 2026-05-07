---
applyTo: "webapp/**/*.py"
---

## API Coding Conventions

- Follow PEP 8 for variables and functions
- PascalCase for class names
- Use type hints for clarity and tooling support
- Add detailed docstrings to endpoint functions
- Include examples in Pydantic model Config
- Use descriptive parameter names and Field descriptions
- Consider async handlers for I/O bound operations
- Configure CORS with specific origins in production
- Use middleware for rate limiting

## Error Handling

- Return appropriate HTTP status codes
- Provide human-readable error messages with actionable information
- Use FastAPI's HTTPException for error responses