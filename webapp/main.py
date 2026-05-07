from os.path import dirname, abspath, join
from os.path import exists

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from webapp.models import GenerateRequest, User, UserCreate, UserUpdate
from webapp.rate_limit import RateLimitMiddleware, SlidingWindowRateLimiter
from webapp.services import TokenService, UserRepository, get_token_service, get_user_repository

current_dir = dirname(abspath(__file__))
static_path = join(current_dir, "static")

app = FastAPI()
app.mount("/ui", StaticFiles(directory=static_path), name="ui")
rate_limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)
app.state.rate_limiter = rate_limiter
app.add_middleware(
    RateLimitMiddleware,
    limiter=rate_limiter,
    excluded_paths={"/docs", "/openapi.json", "/redoc"},
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a consistent JSON payload for unexpected errors."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get('/')
def root():
    """Serve the demo UI."""
    html_path = join(static_path, "index.html")
    if not exists(html_path):
        raise HTTPException(status_code=404, detail="UI not found")

    return FileResponse(html_path)


@app.post('/generate')
def generate(body: GenerateRequest, token_service: TokenService = Depends(get_token_service)):
    """
    Generate a pseudo-random token ID of twenty characters by default. Example POST request body:

    {
        "length": 20
    }
    """
    try:
        token = token_service.generate(body.length)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {'token': token}


@app.post('/users', response_model=User, status_code=201)
def create_user(user_create: UserCreate, repo: UserRepository = Depends(get_user_repository)):
    """Create a new user."""
    user_dict = repo.create(user_create.name, user_create.email)
    return User(**user_dict)


@app.get('/users', response_model=list[User])
def list_users(repo: UserRepository = Depends(get_user_repository)):
    """List all users."""
    users = repo.list_all()
    return [User(**u) for u in users]


@app.get('/users/{user_id}', response_model=User)
def get_user(user_id: int, repo: UserRepository = Depends(get_user_repository)):
    """Get a user by ID."""
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)


@app.put('/users/{user_id}', response_model=User)
def update_user(user_id: int, user_update: UserUpdate, repo: UserRepository = Depends(get_user_repository)):
    """Update a user."""
    user = repo.update(user_id, user_update.name, user_update.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)


@app.delete('/users/{user_id}', status_code=204)
def delete_user(user_id: int, repo: UserRepository = Depends(get_user_repository)):
    """Delete a user."""
    deleted = repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return None


@app.get('/ping')
def ping():
    """Return a simple health response."""
    return {'status': 'ok'}
