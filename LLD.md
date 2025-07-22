# Low-Level Design (LLD) - Little Lemon Restaurant Booking System

## 1. System Architecture Details

### 1.1 Project Structure
```
backend-restaurant-booking-python/
├── src/
│   ├── app.py                          # Main FastAPI application
│   ├── config/                         # Configuration modules
│   │   ├── _database_config.py        # Database configuration
│   │   ├── _jwt_config.py             # JWT configuration
│   │   └── _logger.py                 # Logging configuration
│   ├── controllers/                    # API controllers
│   │   ├── auth_controller.py         # Authentication endpoints
│   │   ├── users_controller.py        # User management endpoints
│   │   ├── bookings_controller.py     # Booking endpoints
│   │   ├── menu_controller.py         # Menu endpoints
│   │   └── admin_controller.py        # Admin endpoints
│   ├── middlewares/                   # Custom middlewares
│   │   ├── jwt_auth.py               # JWT authentication
│   │   ├── admin_auth.py             # Admin authentication
│   │   └── request_logging_middleware.py
│   ├── models/                        # Database models
│   │   ├── user_model.py             # User model
│   │   ├── admin_model.py            # Admin model
│   │   ├── table_model.py            # Table model
│   │   ├── category_model.py         # Category model
│   │   ├── dish_model.py             # Dish model
│   │   ├── booking_model.py          # Booking model
│   │   └── booking_item_model.py     # Booking item model
│   ├── schemas/                       # Pydantic schemas
│   │   ├── auth_schema.py            # Authentication schemas
│   │   ├── user_schema.py            # User schemas
│   │   ├── admin_schema.py           # Admin schemas
│   │   ├── booking_schema.py         # Booking schemas
│   │   └── menu_schema.py            # Menu schemas
│   ├── services/                      # Business logic
│   │   ├── auth_service.py           # Authentication service
│   │   ├── users_service.py          # User service
│   │   ├── admin_service.py          # Admin service
│   │   ├── booking_service.py        # Booking service
│   │   └── menu_service.py           # Menu service
│   ├── repositories/                  # Data access layer
│   │   ├── user_repository.py        # User repository
│   │   ├── admin_repository.py       # Admin repository
│   │   ├── booking_repository.py     # Booking repository
│   │   └── menu_repository.py        # Menu repository
│   ├── utils/                         # Utility functions
│   │   ├── jwt_service.py            # JWT utilities
│   │   └── helpers.py                # Common utilities
│   └── validators/                    # Validation modules
│       ├── common_validator.py       # Common validations
│       ├── email_validator.py        # Email validation
│       ├── password_validator.py     # Password validation
│       └── security_validator.py     # Security validation
├── migrations/                        # Database migrations
├── tests/                            # Test files
├── pyproject.toml                    # Project dependencies
└── README.md                         # Project documentation
```

## 2. Database Schema Design

### 2.1 Detailed Entity Relationships

```mermaid
erDiagram
    USERS {
        int id PK "Primary key"
        string username UK "Unique username"
        string email UK "Unique email"
        string hashed_password "Bcrypt hashed"
        boolean is_active "Account status"
        datetime created_at "Creation timestamp"
        datetime updated_at "Last update timestamp"
    }
    
    ADMINS {
        int id PK "Primary key"
        string username UK "Unique admin username"
        string email UK "Unique admin email"
        string hashed_password "Bcrypt hashed"
        string role "admin, super_admin"
        boolean is_active "Account status"
        datetime created_at "Creation timestamp"
        datetime updated_at "Last update timestamp"
    }
    
    TABLES {
        int id PK "Primary key"
        string table_number UK "Unique table number"
        int capacity "Number of seats"
        string location "Table location"
        boolean is_active "Table availability"
        datetime created_at "Creation timestamp"
        datetime updated_at "Last update timestamp"
    }
    
    CATEGORIES {
        int id PK "Primary key"
        string name "Category name"
        string description "Category description"
        boolean is_active "Category status"
        datetime created_at "Creation timestamp"
        datetime updated_at "Last update timestamp"
    }
    
    DISHES {
        int id PK "Primary key"
        string name "Dish name"
        string description "Dish description"
        decimal price "Dish price"
        int category_id FK "Category reference"
        boolean is_vegetarian "Vegetarian flag"
        boolean is_available "Availability status"
        datetime created_at "Creation timestamp"
        datetime updated_at "Last update timestamp"
    }
    
    BOOKINGS {
        int id PK "Primary key"
        int user_id FK "User reference"
        int table_id FK "Table reference"
        int time_slot_id FK "Time slot reference"
        date booking_date "Booking date"
        int guest_count "Number of guests"
        string status "pending, confirmed, cancelled, completed"
        decimal total_amount "Total booking amount"
        datetime created_at "Creation timestamp"
        datetime updated_at "Last update timestamp"
    }
    
    BOOKING_ITEMS {
        int id PK "Primary key"
        int booking_id FK "Booking reference"
        int dish_id FK "Dish reference"
        int quantity "Item quantity"
        decimal unit_price "Price per unit"
        decimal total_price "Total item price"
        datetime created_at "Creation timestamp"
    }
    
    TIME_SLOTS {
        int id PK "Primary key"
        time start_time "Slot start time"
        time end_time "Slot end time"
        boolean is_active "Slot availability"
        datetime created_at "Creation timestamp"
        datetime updated_at "Last update timestamp"
    }
    
    USERS ||--o{ BOOKINGS : "makes"
    TABLES ||--o{ BOOKINGS : "reserved"
    TIME_SLOTS ||--o{ BOOKINGS : "scheduled"
    CATEGORIES ||--o{ DISHES : "contains"
    BOOKINGS ||--o{ BOOKING_ITEMS : "includes"
    DISHES ||--o{ BOOKING_ITEMS : "ordered"
```


## 3. API Design Specifications

### 3.1 Authentication Endpoints

#### User Registration
```http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "password": "SecureP@ss123"
}

Response:
{
  "data": {
    "token": "jwt_token_here",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john.doe@example.com",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  },
  "message": "User created successfully.",
  "status": true
}
```

#### User Login
```http
POST /api/v1/auth/signin
Content-Type: application/json

{
  "email": "john.doe@example.com",
  "password": "SecureP@ss123"
}

Response:
{
  "data": {
    "token": "jwt_token_here",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john.doe@example.com",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  },
  "message": "User signed in successfully.",
  "status": true
}
```

### 3.2 Booking Endpoints

#### Create Booking
```http
POST /api/v1/bookings
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "table_id": 1,
  "time_slot_id": 1,
  "booking_date": "2024-01-15",
  "guest_count": 4,
  "dishes": [
    {
      "dish_id": 1,
      "quantity": 2
    },
    {
      "dish_id": 3,
      "quantity": 1
    }
  ]
}

Response:
{
  "data": {
    "id": 1,
    "user_id": 1,
    "table_id": 1,
    "time_slot_id": 1,
    "booking_date": "2024-01-15",
    "guest_count": 4,
    "status": "confirmed",
    "total_amount": 85.50,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  },
  "message": "Booking created successfully.",
  "status": true
}
```

#### Update Booking
```http
PUT /api/v1/bookings/{id}
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "booking_date": "2024-01-15",
  "time_slot_id": 2,
  "guest_count": 6,
  "status": "cancelled",
  "dishes": [
    {
      "dish_id": 1,
      "quantity": 3
    }
  ]
}

Response:
{
  "data": {
    "id": 1,
    "user_id": 1,
    "table_id": 1,
    "time_slot_id": 2,
    "booking_date": "2024-01-15",
    "guest_count": 6,
    "status": "cancelled",
    "total_amount": 95.50,
    "updated_at": "2024-01-01T10:00:00Z"
  },
  "message": "Booking updated successfully.",
  "status": true
}
```

### 3.3 Menu Endpoints

#### Get Categories
```http
GET /api/v1/menu/categories

Response:
{
  "data": [
    {
      "id": 1,
      "name": "Appetizers",
      "description": "Start your meal with our delicious appetizers",
      "is_active": true
    },
    {
      "id": 2,
      "name": "Main Course",
      "description": "Our signature main dishes",
      "is_active": true
    }
  ],
  "message": "Categories retrieved successfully.",
  "status": true
}
```

#### Get Dishes
```http
GET /api/v1/menu/dishes?category_id=1

Response:
{
  "data": [
    {
      "id": 1,
      "name": "Bruschetta",
      "description": "Toasted bread with tomatoes and herbs",
      "price": 8.50,
      "category_id": 1,
      "is_vegetarian": true,
      "is_available": true
    }
  ],
  "message": "Dishes retrieved successfully.",
  "status": true
}
```

### 3.4 Admin Endpoints

#### Admin Login
```http
POST /api/v1/admin/auth/signin
Content-Type: application/json

{
  "username": "admin",
  "password": "AdminP@ss123"
}

Response:
{
  "data": {
    "token": "admin_jwt_token_here",
    "admin": {
      "id": 1,
      "username": "admin",
      "email": "admin@littlelemon.com",
      "role": "admin",
      "is_active": true
    }
  },
  "message": "Admin signed in successfully.",
  "status": true
}
```

#### Get All Bookings (Admin)
```http
GET /api/v1/admin/bookings?status=confirmed&date=2024-01-15
Authorization: Bearer <admin_jwt_token>

Response:
{
  "data": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john.doe@example.com"
      },
      "table": {
        "id": 1,
        "table_number": "T01",
        "capacity": 4
      },
      "booking_date": "2024-01-15",
      "time_slot_id": 1,
      "guest_count": 4,
      "status": "confirmed",
      "total_amount": 85.50
    }
  ],
  "message": "Bookings retrieved successfully.",
  "status": true
}
```

## 4. Service Layer Implementation

### 4.1 Authentication Service Flow

```mermaid
flowchart TD
    A[User Registration Request] --> B[Validate Input Data]
    B --> C{Validation Passed?}
    C -->|No| D[Return Validation Error]
    C -->|Yes| E[Check Email/Username Exists]
    E --> F{Already Exists?}
    F -->|Yes| G[Return Conflict Error]
    F -->|No| H[Hash Password]
    H --> I[Create User Record]
    I --> J[Generate JWT Token]
    J --> K[Return Success Response]
```

### 4.2 Booking Service Flow

```mermaid
flowchart TD
    A[Booking Request] --> B[Validate User Token]
    B --> C{Token Valid?}
    C -->|No| D[Return Unauthorized]
    C -->|Yes| E[Check Table & Time Slot Availability]
    E --> F{Available?}
    F -->|No| G[Return Conflict Error]
    F -->|Yes| H[Get Menu Items]
    H --> I[Calculate Total Amount]
    I --> J[Create Booking Record]
    J --> K[Create Booking Items]
    K --> L[Update Table Status]
    L --> M[Return Success Response]
```

## 5. Middleware Implementation

### 5.1 JWT Authentication Middleware
```python
async def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user"""
    payload = await verify_jwt_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return await get_user_by_id(user_id)
```

### 5.2 Admin Authentication Middleware
```python
async def get_current_admin(token: str = Depends(oauth2_scheme)) -> Admin:
    """Get current authenticated admin"""
    payload = await verify_jwt_token(token)
    admin_id = payload.get("sub")
    role = payload.get("role")
    
    if admin_id is None or role != "admin":
        raise HTTPException(status_code=401, detail="Admin access required")
    
    return await get_admin_by_id(admin_id)
```

## 6. Error Handling Strategy

### 6.1 HTTP Status Codes
- `200 OK`: Successful operation
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., booking conflict)
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### 6.2 Error Response Format
```json
{
  "message": "Error description",
  "status": false,
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 6.3 Common Error Response Examples

#### 400 Bad Request - Validation Error
```json
{
  "message": "Validation failed",
  "status": false,
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    },
    {
      "field": "password",
      "message": "Password must be at least 8 characters"
    }
  ]
}
```

#### 401 Unauthorized - Invalid Token
```json
{
  "message": "Invalid authentication credentials",
  "status": false,
  "data": null
}
```

#### 404 Not Found - Resource Not Found
```json
{
  "message": "Booking not found",
  "status": false,
  "data": null
}
```

#### 409 Conflict - Booking Conflict
```json
{
  "message": "Table is not available for the selected time slot",
  "status": false,
  "data": null
}
```

#### 422 Unprocessable Entity - Business Logic Error
```json
{
  "message": "Cannot cancel booking less than 2 hours before start time",
  "status": false,
  "data": null
}
```

#### 500 Internal Server Error
```json
{
  "message": "An unexpected error occurred",
  "status": false,
  "data": null
}
```

## 7. Data Validation Rules

### 7.1 User Registration Validation
- Username: 3-30 characters, alphanumeric + underscore
- Email: Valid email format
- Password: Minimum 8 characters, uppercase, lowercase, number, special character

### 7.2 Booking Validation
- Booking date: Future date only
- Time slots: Within restaurant hours (11:00-23:00)
- Guest count: 1-10 people per table
- Table availability: No double booking
- Minimum notice: 2 hours advance booking

### 7.3 Menu Validation
- Dish name: 2-100 characters
- Price: Positive decimal value
- Category: Must exist and be active
- Availability: Boolean flag

## 8. Security Implementation

### 8.1 Password Security
```python
# Password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 8.2 JWT Token Security
```python
# JWT configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

## 9. Database Operations

### 9.1 Connection Pooling
```python
# Database configuration
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 9.2 Transaction Management
```python
async def create_booking_with_items(booking_data: dict, items: list):
    async with db_session() as session:
        async with session.begin():
            # Create booking
            booking = Booking(**booking_data)
            session.add(booking)
            await session.flush()
            
            # Create booking items
            for item in items:
                booking_item = BookingItem(
                    booking_id=booking.id,
                    **item
                )
                session.add(booking_item)
            
            await session.commit()
            return booking
```

## 10. Testing Strategy

### 10.1 Unit Tests
- Service layer business logic
- Repository data access methods
- Utility functions
- Validation functions

### 10.2 Integration Tests
- API endpoint testing
- Database integration
- Authentication flow
- Booking workflow



## 11. Deployment Configuration

### 11.1 Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/little_lemon
SQLALCHEMY_ECHO_SQL=false

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 11.2 Docker Configuration
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 12. Monitoring and Logging

### 12.1 Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 12.2 Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## 13. Performance Optimization

### 13.1 Database Query Optimization
- Use indexes on frequently queried columns
- Implement pagination for large datasets
- Use select() to fetch only required columns
- Implement connection pooling

### 13.2 API Response Optimization
- Implement response caching
- Use async/await for I/O operations
- Compress responses for large datasets
- Implement pagination for list endpoints

## 14. Implementation Timeline

### Phase 1 (Week 1): Core Setup
- ✅ User authentication system (already implemented)
- ✅ Basic API structure (already implemented)
- Database schema implementation (remaining tables)
- Admin user management
- Admin authentication middleware

### Phase 2 (Week 2): Menu & Tables
- Menu categories and dishes
- Table management
- Availability tracking
- Basic CRUD operations

### Phase 3 (Week 3): Booking System
- Complete booking workflow
- Conflict resolution
- Status management
- Booking history

### Phase 4 (Week 4): Admin Features + Testing
- Admin dashboard endpoints
- Analytics and reporting
- Comprehensive testing
- Performance optimization 