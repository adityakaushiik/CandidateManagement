from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.repository_deps import get_user_repository, get_current_user
from repositories.user_repository import UserRepository
from models.user_model import UserCreate, UserResponse, LoginRequest, LoginResponse
from utils.common_constants import UserRoles
from utils.security import hash_password, verify_password
from config.jwt_utils import create_access_token

auth_route = APIRouter()


@auth_route.post("/register/candidate", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_candidate(user: UserCreate, repo: UserRepository = Depends(get_user_repository)):
    """
    Register a new candidate user.
    This endpoint is publicly accessible and only allows creating candidate accounts.
    """
    # Force role to be candidate
    if user.role_id != UserRoles.CANDIDATE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint only allows candidate registration"
        )

    existing = await repo.get_by_email(user.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
        hashed = hash_password(user.password)
        created = await repo.create(hashed, user)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering candidate: {str(e)}"
        )


@auth_route.post("/register/sub-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_sub_admin(
    user: UserCreate,
    current_user: dict = Depends(get_current_user),
    repo: UserRepository = Depends(get_user_repository)
):
    """
    Register a new sub-admin user.
    This endpoint is only accessible to admin users.
    """
    # Check if current user is an admin
    user_roles = current_user.get("roles", [])
    if UserRoles.ADMIN.value not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can register sub-admin users"
        )

    # Force role to be sub-admin
    if user.role_id != UserRoles.SUB_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint only allows sub-admin registration"
        )

    existing = await repo.get_by_email(user.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
        hashed = hash_password(user.password)
        created = await repo.create(hashed, user)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering sub-admin: {str(e)}"
        )


@auth_route.post("/register/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(
    user: UserCreate,
    current_user: dict = Depends(get_current_user),
    repo: UserRepository = Depends(get_user_repository)
):
    """
    Register a new admin user.
    This endpoint is only accessible to existing admin users.
    """
    # Check if current user is an admin
    user_roles = current_user.get("roles", [])
    if UserRoles.ADMIN.value not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can register new admin users"
        )

    # Force role to be admin
    if user.role_id != UserRoles.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint only allows admin registration"
        )

    existing = await repo.get_by_email(user.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
        hashed = hash_password(user.password)
        created = await repo.create(hashed, user)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering admin: {str(e)}"
        )


@auth_route.post("/setup/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def setup_initial_admin(
    user: UserCreate,
    repo: UserRepository = Depends(get_user_repository)
):
    """
    Create the first admin user for initial system setup.
    This endpoint only works if no admin users exist in the system.
    After the first admin is created, use /register/admin endpoint instead.
    """
    # Force role to be admin
    if user.role_id != UserRoles.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint only allows admin registration"
        )

    # Check if any admin already exists
    existing_admin = await repo.collection.find_one({"role_id": UserRoles.ADMIN.value})
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin already exists. Use /register/admin endpoint with admin authentication instead."
        )

    existing = await repo.get_by_email(user.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
        hashed = hash_password(user.password)
        created = await repo.create(hashed, user)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating initial admin: {str(e)}"
        )


@auth_route.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, repo: UserRepository = Depends(get_user_repository)):
    doc = await repo.get_by_email(payload.email)
    if not doc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    stored_hash = doc.get("password_hash")
    # Support legacy plaintext migration
    if not stored_hash:
        legacy_plain = doc.get("password")
        if legacy_plain and legacy_plain == payload.password:
            # Hash and save immediately
            new_hash = hash_password(payload.password)
            await repo.update_password_hash(str(doc["_id"]), new_hash)
            stored_hash = new_hash
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(payload.password, stored_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Always re-hash and save the password on successful login (per requirement)
    try:
        new_hash = hash_password(payload.password)
        await repo.update_password_hash(str(doc["_id"]), new_hash)
    except Exception:
        # Do not block login on save failure
        pass

    token = create_access_token(
        {
            "sub": str(doc["_id"]),
            "email": doc.get("email"),
            "roles": [int(doc.get("role_id", 0))],
            "name": doc.get("name"),
        }
    )

    # Create user response from the document
    user_response = UserResponse.from_mongo(doc)

    return LoginResponse(access_token=token, user=user_response)
