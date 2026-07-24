"""Authentication utilities for Echo Prayer MCP Server"""
import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from src.logging import logger, log_error_with_context

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthManager:
    """Manages user authentication and session handling"""
    
    def __init__(self, db_path: str = "data/db/users.db"):
        self.db_path = db_path
        self._init_user_db()
    
    def _init_user_db(self):
        """Initialize the users database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Create users table
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    hashed_password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Create prayer_shares table for tracking shared prayers
            c.execute('''
                CREATE TABLE IF NOT EXISTS prayer_shares (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    prayer_id INTEGER NOT NULL,
                    shared_with_user_id INTEGER,
                    shared_with_group TEXT,
                    share_type TEXT NOT NULL CHECK (share_type IN ('private', 'public')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (shared_with_user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("User database initialized successfully")
            
        except Exception as e:
            log_error_with_context(e, {"operation": "init_user_db"})
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        # bcrypt has a 72-byte limit, so truncate if necessary
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        # bcrypt has a 72-byte limit, so truncate if necessary
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, username: str, password: str, email: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Check if user already exists
            c.execute("SELECT id FROM users WHERE username = ?", (username,))
            if c.fetchone():
                conn.close()
                return {"success": False, "error": "Username already exists"}
            
            # Hash password and create user
            hashed_password = self.hash_password(password)
            c.execute(
                "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
                (username, email, hashed_password)
            )
            
            user_id = c.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"User created successfully: {username}")
            return {"success": True, "user_id": user_id, "username": username}
            
        except Exception as e:
            log_error_with_context(e, {"operation": "create_user", "username": username})
            return {"success": False, "error": "Failed to create user"}
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return user info"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute(
                "SELECT id, username, email, hashed_password FROM users WHERE username = ?",
                (username,)
            )
            user = c.fetchone()
            
            if not user or not self.verify_password(password, user[3]):
                conn.close()
                return None
            
            # Update last login
            c.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user[0],)
            )
            conn.commit()
            conn.close()
            
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2]
            }
            
        except Exception as e:
            log_error_with_context(e, {"operation": "authenticate_user", "username": username})
            return None
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token and return user info"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            
            # Get fresh user data from database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                "SELECT id, username, email FROM users WHERE username = ?",
                (username,)
            )
            user = c.fetchone()
            conn.close()
            
            if user is None:
                return None
            
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2]
            }
            
        except JWTError as e:
            log_error_with_context(e, {"operation": "verify_token"})
            return None
    
    def share_prayer(self, user_id: int, prayer_id: int, share_type: str, 
                    shared_with_user_id: Optional[int] = None, 
                    shared_with_group: Optional[str] = None) -> Dict[str, Any]:
        """Share a prayer with another user or group"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute(
                """INSERT INTO prayer_shares 
                   (user_id, prayer_id, share_type, shared_with_user_id, shared_with_group) 
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, prayer_id, share_type, shared_with_user_id, shared_with_group)
            )
            
            share_id = c.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Prayer shared successfully: user {user_id} shared prayer {prayer_id}")
            return {"success": True, "share_id": share_id}
            
        except Exception as e:
            log_error_with_context(e, {"operation": "share_prayer", "user_id": user_id, "prayer_id": prayer_id})
            return {"success": False, "error": "Failed to share prayer"}
    
    def get_user_shared_prayers(self, user_id: int) -> list:
        """Get all prayers shared by a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute(
                """SELECT ps.id, ps.prayer_id, ps.share_type, ps.shared_with_user_id, 
                          ps.shared_with_group, ps.created_at, u.username
                   FROM prayer_shares ps
                   LEFT JOIN users u ON ps.shared_with_user_id = u.id
                   WHERE ps.user_id = ?
                   ORDER BY ps.created_at DESC""",
                (user_id,)
            )
            
            shares = c.fetchall()
            conn.close()
            
            return [
                {
                    "share_id": share[0],
                    "prayer_id": share[1],
                    "share_type": share[2],
                    "shared_with_user_id": share[3],
                    "shared_with_group": share[4],
                    "created_at": share[5],
                    "shared_with_username": share[6]
                }
                for share in shares
            ]
            
        except Exception as e:
            log_error_with_context(e, {"operation": "get_user_shared_prayers", "user_id": user_id})
            return []
    
    def get_prayers_shared_with_user(self, user_id: int) -> list:
        """Get all prayers shared with a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute(
                """SELECT ps.id, ps.prayer_id, ps.share_type, ps.shared_with_group, 
                          ps.created_at, u.username
                   FROM prayer_shares ps
                   JOIN users u ON ps.user_id = u.id
                   WHERE ps.shared_with_user_id = ? OR ps.share_type = 'public'
                   ORDER BY ps.created_at DESC""",
                (user_id,)
            )
            
            shares = c.fetchall()
            conn.close()
            
            return [
                {
                    "share_id": share[0],
                    "prayer_id": share[1],
                    "share_type": share[2],
                    "shared_with_group": share[3],
                    "created_at": share[4],
                    "shared_by_username": share[5]
                }
                for share in shares
            ]
            
        except Exception as e:
            log_error_with_context(e, {"operation": "get_prayers_shared_with_user", "user_id": user_id})
            return []

# Global auth manager instance
auth_manager = AuthManager()
