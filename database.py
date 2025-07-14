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

engine = sa.create_engine(DATABASE_URL)
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

# Database functions
def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def close_db(db):
    """Close database session"""
    db.close()

def save_emotion_analysis(session_id, expressions, ai_analysis, analysis_type="demo", confidence=None):
    """
    Save emotion analysis to database
    
    Args:
        session_id (str): User session ID
        expressions (list): List of detected expressions
        ai_analysis (str): AI-generated analysis
        analysis_type (str): Type of analysis ('webcam', 'image', 'demo')
        confidence (float): Confidence score if available
    
    Returns:
        bool: Success status
    """
    try:
        db = get_db()
        
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
        close_db(db)
        return True
        
    except Exception as e:
        print(f"Database error: {e}")
        if 'db' in locals():
            db.rollback()
            close_db(db)
        return False

def get_user_history(session_id, limit=10):
    """
    Get user's emotion analysis history
    
    Args:
        session_id (str): User session ID
        limit (int): Number of recent analyses to retrieve
    
    Returns:
        list: List of analysis records
    """
    try:
        db = get_db()
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
        
        close_db(db)
        return result
        
    except Exception as e:
        print(f"Database error: {e}")
        if 'db' in locals():
            close_db(db)
        return []

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