import os
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = sa.create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_size=5,         # Number of connections to maintain
    max_overflow=10,     # Maximum overflow connections
    connect_args={
        "connect_timeout": 30
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class EmotionAnalysis(Base):
    __tablename__ = "emotion_analysis"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    session_id = sa.Column(sa.String(100), index=True)
    timestamp = sa.Column(sa.DateTime, default=datetime.utcnow)
    detected_expressions = sa.Column(sa.Text)  # JSON string of detected expressions
    ai_analysis = sa.Column(sa.Text)
    analysis_type = sa.Column(sa.String(50))  # 'webcam', 'image', 'demo'
    confidence_score = sa.Column(sa.Float, nullable=True)
    
class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    session_id = sa.Column(sa.String(100), unique=True, index=True)
    start_time = sa.Column(sa.DateTime, default=datetime.utcnow)
    last_activity = sa.Column(sa.DateTime, default=datetime.utcnow)
    total_analyses = sa.Column(sa.Integer, default=0)
    
class ExpressionStats(Base):
    __tablename__ = "expression_stats"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    expression_name = sa.Column(sa.String(100), index=True)
    detection_count = sa.Column(sa.Integer, default=0)
    last_detected = sa.Column(sa.DateTime, default=datetime.utcnow)
    avg_confidence = sa.Column(sa.Float, nullable=True)

class User(Base):
    __tablename__ = "users"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    email = sa.Column(sa.String(255), unique=True, index=True, nullable=False)
    password_hash = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    last_login = sa.Column(sa.DateTime, nullable=True)
    is_active = sa.Column(sa.Boolean, default=True)
    
class UserLogin(Base):
    __tablename__ = "user_logins"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    session_token = sa.Column(sa.String(255), unique=True, index=True, nullable=False)
    login_time = sa.Column(sa.DateTime, default=datetime.utcnow)
    expires_at = sa.Column(sa.DateTime, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True)

# Database functions
def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test the connection
            db.execute(sa.text("SELECT 1"))
            return db
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            if db:
                db.close()

def close_db(db):
    """Close database session safely"""
    try:
        if db:
            db.close()
    except Exception as e:
        print(f"Error closing database connection: {e}")

def safe_db_operation(operation_func, *args, **kwargs):
    """Execute database operation with automatic retry and error handling"""
    max_retries = 3
    for attempt in range(max_retries):
        db = None
        try:
            db = get_db()
            result = operation_func(db, *args, **kwargs)
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Database operation failed after {max_retries} attempts: {e}")
                return False
            print(f"Database operation attempt {attempt + 1} failed: {e}")
        finally:
            close_db(db)

def _save_emotion_analysis_impl(db, session_id, expressions, ai_analysis, analysis_type="demo", confidence=None):
    """Internal implementation of save_emotion_analysis"""
    # Save the analysis
    analysis = EmotionAnalysis(
        session_id=session_id,
        detected_expressions=json.dumps(expressions),
        ai_analysis=ai_analysis,
        analysis_type=analysis_type,
        confidence_score=confidence
    )
    db.add(analysis)
    
    # Update or create user session
    user_session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
    if user_session:
        user_session.last_activity = datetime.utcnow()
        user_session.total_analyses += 1
    else:
        user_session = UserSession(
            session_id=session_id,
            total_analyses=1
        )
        db.add(user_session)
    
    # Update expression statistics
    for expr in expressions:
        expr_stat = db.query(ExpressionStats).filter(ExpressionStats.expression_name == expr).first()
        if expr_stat:
            expr_stat.detection_count += 1
            expr_stat.last_detected = datetime.utcnow()
            if confidence:
                expr_stat.avg_confidence = ((expr_stat.avg_confidence or 0) + confidence) / 2
        else:
            expr_stat = ExpressionStats(
                expression_name=expr,
                detection_count=1,
                avg_confidence=confidence
            )
            db.add(expr_stat)
    
    db.commit()
    return True

def save_emotion_analysis(session_id, expressions, ai_analysis, analysis_type="demo", confidence=None):
    """
    Save emotion analysis to database with retry logic
    
    Args:
        session_id (str): User session ID
        expressions (list): List of detected expressions
        ai_analysis (str): AI-generated analysis
        analysis_type (str): Type of analysis ('webcam', 'image', 'demo')
        confidence (float): Confidence score if available
    
    Returns:
        bool: Success status
    """
    return safe_db_operation(
        _save_emotion_analysis_impl,
        session_id, expressions, ai_analysis, analysis_type, confidence
    )

def _get_user_history_impl(db, session_id, limit=10):
    """Internal implementation of get_user_history"""
    analyses = db.query(EmotionAnalysis).filter(
        EmotionAnalysis.session_id == session_id
    ).order_by(EmotionAnalysis.timestamp.desc()).limit(limit).all()
    
    result = []
    for analysis in analyses:
        result.append({
            'timestamp': analysis.timestamp,
            'expressions': json.loads(analysis.detected_expressions),
            'ai_analysis': analysis.ai_analysis,
            'analysis_type': analysis.analysis_type,
            'confidence': analysis.confidence_score
        })
    
    return result

def get_user_history(session_id, limit=10):
    """
    Get user's emotion analysis history with retry logic
    
    Args:
        session_id (str): User session ID
        limit (int): Number of recent analyses to retrieve
    
    Returns:
        list: List of analysis records
    """
    result = safe_db_operation(_get_user_history_impl, session_id, limit)
    return result if result else []

def get_expression_statistics():
    """
    Get overall expression statistics
    
    Returns:
        dict: Statistics about detected expressions
    """
    try:
        db = get_db()
        
        # Get top expressions
        top_expressions = db.query(ExpressionStats).order_by(
            ExpressionStats.detection_count.desc()
        ).limit(10).all()
        
        # Get total analyses
        total_analyses = db.query(EmotionAnalysis).count()
        
        # Get unique users
        unique_users = db.query(UserSession).count()
        
        result = {
            'total_analyses': total_analyses,
            'unique_users': unique_users,
            'top_expressions': [
                {
                    'name': expr.expression_name,
                    'count': expr.detection_count,
                    'avg_confidence': expr.avg_confidence
                }
                for expr in top_expressions
            ]
        }
        
        close_db(db)
        return result
        
    except Exception as e:
        print(f"Database error: {e}")
        if 'db' in locals():
            close_db(db)
        return {'total_analyses': 0, 'unique_users': 0, 'top_expressions': []}

def get_emotion_trends(days=7):
    """
    Get emotion trends over time
    
    Args:
        days (int): Number of days to analyze
    
    Returns:
        dict: Trend data
    """
    try:
        db = get_db()
        
        # Get analyses from last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_analyses = db.query(EmotionAnalysis).filter(
            EmotionAnalysis.timestamp >= cutoff_date
        ).all()
        
        # Process trend data
        daily_counts = {}
        expression_trends = {}
        
        for analysis in recent_analyses:
            date_key = analysis.timestamp.strftime('%Y-%m-%d')
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
            
            expressions = json.loads(analysis.detected_expressions)
            for expr in expressions:
                if expr not in expression_trends:
                    expression_trends[expr] = {}
                expression_trends[expr][date_key] = expression_trends[expr].get(date_key, 0) + 1
        
        close_db(db)
        return {
            'daily_counts': daily_counts,
            'expression_trends': expression_trends
        }
        
    except Exception as e:
        print(f"Database error: {e}")
        if 'db' in locals():
            close_db(db)
        return {'daily_counts': {}, 'expression_trends': {}}