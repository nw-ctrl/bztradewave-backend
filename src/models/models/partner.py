from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

class PartnerStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class BusinessType(enum.Enum):
    IMPORT_EXPORT = "Import/Export Company"
    MANUFACTURING = "Manufacturing"
    AGRICULTURE = "Agriculture"
    ELECTRONICS = "Electronics"
    FASHION = "Fashion/Textiles"
    TECHNOLOGY = "Technology Services"
    LOGISTICS = "Logistics/Shipping"
    FINANCIAL = "Financial Services"
    OTHER = "Other"

class Partner(db.Model):
    __tablename__ = 'partners'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Company Information
    company_name = db.Column(db.String(200), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    
    # Business Details
    business_type = db.Column(db.Enum(BusinessType), nullable=False)
    annual_revenue = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    interests = db.Column(db.Text)
    message = db.Column(db.Text)
    
    # Authentication
    password_hash = db.Column(db.String(255))
    
    # Status and Metadata
    status = db.Column(db.Enum(PartnerStatus), default=PartnerStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    
    # Activity tracking
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    
    # Relationships
    messages = db.relationship('Message', backref='partner', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='partner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert partner to dictionary"""
        data = {
            'id': self.id,
            'company_name': self.company_name,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone,
            'country': self.country,
            'business_type': self.business_type.value if self.business_type else None,
            'annual_revenue': self.annual_revenue,
            'experience': self.experience,
            'interests': self.interests,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count
        }
        
        if include_sensitive:
            data['message'] = self.message
            
        return data
    
    def __repr__(self):
        return f'<Partner {self.company_name} ({self.email})>'


class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert admin to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<Admin {self.username}>'


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    sender_type = db.Column(db.String(20), nullable=False)  # 'partner' or 'admin'
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'admin_id': self.admin_id,
            'sender_type': self.sender_type,
            'subject': self.subject,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Message {self.id} from {self.sender_type}>'


class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_shared = db.Column(db.Boolean, default=False, nullable=False)
    uploaded_by_type = db.Column(db.String(20), nullable=False)  # 'partner' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'admin_id': self.admin_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'description': self.description,
            'is_shared': self.is_shared,
            'uploaded_by_type': self.uploaded_by_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'


class MarketInsight(db.Model):
    __tablename__ = 'market_insights'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # agriculture, electronics, fashion
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    confidence_level = db.Column(db.String(20), nullable=False)  # high, medium, low
    data_source = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def to_dict(self):
        """Convert market insight to dictionary"""
        return {
            'id': self.id,
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'confidence_level': self.confidence_level,
            'data_source': self.data_source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<MarketInsight {self.title}>'


class NewsArticle(db.Model):
    __tablename__ = 'news_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    source_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    published_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    
    def to_dict(self):
        """Convert news article to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'content': self.content,
            'category': self.category,
            'source_url': self.source_url,
            'image_url': self.image_url,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_featured': self.is_featured
        }
    
    def __repr__(self):
        return f'<NewsArticle {self.title}>'

