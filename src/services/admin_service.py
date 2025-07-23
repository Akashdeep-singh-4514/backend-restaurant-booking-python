from src.schemas.admin_schema import AdminCreate, AdminUpdate, AdminLogin, AdminResponse
from src.models.admin_model import Admin
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.config._database_config import logger
from passlib.context import CryptContext
from src.validators import CommonValidator, EmailValidator, PasswordValidator, SecurityValidator

class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logger
        # Password encryption context
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_admin(self, admin: AdminCreate)->AdminResponse:
        """Create a new admin."""
        async with self.db as session:
            admin_data = admin.model_dump()
            CommonValidator.validate_required_fields(admin_data, ["username", "email", "password", "role"])
            admin_data['email'] = SecurityValidator.sanitize_string(admin_data['email'])
            EmailValidator.is_valid_email(admin_data["email"])
            admin_data['username'] = SecurityValidator.sanitize_string(admin_data['username'])
            admin_data['password'] = SecurityValidator.sanitize_string(admin_data['password'])
            PasswordValidator.validate_password(admin_data["password"])
            if not PasswordValidator.is_strong_password(admin_data['password']):
                raise ValueError("Password is not strong enough")
            admin_data['password'] = self.hash_password(admin_data['password'])
            admin_data['is_active'] = True
            admin_data['created_at'] = datetime.now()
            admin_data['updated_at'] = datetime.now()
            admin = Admin(**admin_data)
            existing_admin = await session.execute(select(AdminLogin).where(AdminLogin.username == admin.username or AdminLogin.email == admin.email))
            if existing_admin:
                raise ValueError(f"Admin with {admin_data['username'] == existing_admin.username if 'username' in admin_data else 'email'} already exists")
            
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            return AdminResponse.model_validate(admin)


    