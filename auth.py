import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database import get_db, close_db, User, UserLogin
import sqlalchemy as sa

class AuthSystem:
    def __init__(self):
        self.session_duration = timedelta(days=30)  # 30-day session
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, password_hash = stored_hash.split(':')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return test_hash == password_hash
        except:
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def register_user(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        db = get_db()
        if not db:
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            # Validate email format
            if not self.validate_email(email):
                return {'success': False, 'error': 'Invalid email format'}
            
            # Validate password strength
            password_validation = self.validate_password(password)
            if not password_validation['valid']:
                return {
                    'success': False, 
                    'error': 'Password requirements not met',
                    'details': password_validation['errors']
                }
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email.lower()).first()
            if existing_user:
                return {'success': False, 'error': 'Email already registered'}
            
            # Create new user
            password_hash = self.hash_password(password)
            new_user = User(
                email=email.lower(),
                password_hash=password_hash,
                created_at=datetime.utcnow(),
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user_id': new_user.id
            }
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': f'Registration failed: {str(e)}'}
        finally:
            close_db(db)
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and create session"""
        db = get_db()
        if not db:
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            # Find user
            user = db.query(User).filter(User.email == email.lower()).first()
            if not user:
                return {'success': False, 'error': 'Invalid email or password'}
            
            if not user.is_active:
                return {'success': False, 'error': 'Account is deactivated'}
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                return {'success': False, 'error': 'Invalid email or password'}
            
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + self.session_duration
            
            # Create login session
            login_session = UserLogin(
                user_id=user.id,
                session_token=session_token,
                login_time=datetime.utcnow(),
                expires_at=expires_at,
                is_active=True
            )
            
            db.add(login_session)
            
            # Update user's last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            return {
                'success': True,
                'message': 'Login successful',
                'session_token': session_token,
                'user_id': user.id,
                'email': user.email,
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': f'Login failed: {str(e)}'}
        finally:
            close_db(db)
    
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validate user session token"""
        db = get_db()
        if not db:
            return {'valid': False, 'error': 'Database connection failed'}
        
        try:
            # Find active session
            session = db.query(UserLogin).filter(
                UserLogin.session_token == session_token,
                UserLogin.is_active == True,
                UserLogin.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                return {'valid': False, 'error': 'Invalid or expired session'}
            
            # Get user info
            user = db.query(User).filter(User.id == session.user_id).first()
            if not user or not user.is_active:
                return {'valid': False, 'error': 'User not found or inactive'}
            
            return {
                'valid': True,
                'user_id': user.id,
                'email': user.email,
                'session_expires': session.expires_at.isoformat()
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Session validation failed: {str(e)}'}
        finally:
            close_db(db)
    
    def logout_user(self, session_token: str) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        db = get_db()
        if not db:
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            # Find and deactivate session
            session = db.query(UserLogin).filter(
                UserLogin.session_token == session_token,
                UserLogin.is_active == True
            ).first()
            
            if session:
                session.is_active = False
                db.commit()
                return {'success': True, 'message': 'Logged out successfully'}
            else:
                return {'success': False, 'error': 'Session not found'}
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': f'Logout failed: {str(e)}'}
        finally:
            close_db(db)
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """Get user information"""
        db = get_db()
        if not db:
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'is_active': user.is_active
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get user info: {str(e)}'}
        finally:
            close_db(db)
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        db = get_db()
        if not db:
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            # Find user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Verify current password
            if not self.verify_password(current_password, user.password_hash):
                return {'success': False, 'error': 'Current password is incorrect'}
            
            # Validate new password
            password_validation = self.validate_password(new_password)
            if not password_validation['valid']:
                return {
                    'success': False,
                    'error': 'New password requirements not met',
                    'details': password_validation['errors']
                }
            
            # Update password
            user.password_hash = self.hash_password(new_password)
            db.commit()
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': f'Password change failed: {str(e)}'}
        finally:
            close_db(db)
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        db = get_db()
        if not db:
            return
        
        try:
            expired_sessions = db.query(UserLogin).filter(
                UserLogin.expires_at < datetime.utcnow(),
                UserLogin.is_active == True
            ).all()
            
            for session in expired_sessions:
                session.is_active = False
            
            db.commit()
            
        except Exception as e:
            db.rollback()
        finally:
            close_db(db)

# Global auth instance
auth_system = AuthSystem()