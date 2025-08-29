from flask import Blueprint, request, jsonify, current_app
from src.models.partner import db, Partner, Admin, PartnerStatus
from datetime import datetime, timedelta
import jwt
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def generate_token(user_id, user_type, email):
    """Generate JWT token for authentication"""
    payload = {
        'user_id': user_id,
        'user_type': user_type,  # 'partner' or 'admin'
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user_type = data['user_type']
            current_user_email = data['email']
            
            # Add user info to request context
            request.current_user = {
                'id': current_user_id,
                'type': current_user_type,
                'email': current_user_email
            }
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'current_user') or request.current_user['type'] != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    
    return decorated

@auth_bp.route('/partner/register', methods=['POST'])
def partner_register():
    """Register a new partner application"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['company_name', 'contact_name', 'email', 'phone', 'country', 
                          'business_type', 'annual_revenue', 'experience']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        existing_partner = Partner.query.filter_by(email=data['email']).first()
        if existing_partner:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new partner
        partner = Partner(
            company_name=data['company_name'],
            contact_name=data['contact_name'],
            email=data['email'],
            phone=data['phone'],
            country=data['country'],
            business_type=data['business_type'],
            annual_revenue=data['annual_revenue'],
            experience=data['experience'],
            interests=data.get('interests', ''),
            message=data.get('message', ''),
            status=PartnerStatus.PENDING
        )
        
        db.session.add(partner)
        db.session.commit()
        
        return jsonify({
            'message': 'Partnership application submitted successfully',
            'partner_id': partner.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/partner/login', methods=['POST'])
def partner_login():
    """Partner login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find partner by email
        partner = Partner.query.filter_by(email=email).first()
        
        if not partner:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if partner is approved
        if partner.status != PartnerStatus.APPROVED:
            status_messages = {
                PartnerStatus.PENDING: 'Your application is still pending approval',
                PartnerStatus.REJECTED: 'Your application has been rejected',
                PartnerStatus.SUSPENDED: 'Your account has been suspended'
            }
            return jsonify({'error': status_messages.get(partner.status, 'Account not active')}), 401
        
        # For demo purposes, allow login without password if no password is set
        if not partner.password_hash:
            # Set a default password for demo
            partner.set_password('demo123')
            db.session.commit()
        
        # Check password
        if not partner.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update login tracking
        partner.last_login = datetime.utcnow()
        partner.login_count += 1
        db.session.commit()
        
        # Generate token
        token = generate_token(partner.id, 'partner', partner.email)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'partner': partner.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find admin by username or email
        admin = Admin.query.filter(
            (Admin.username == username) | (Admin.email == username)
        ).first()
        
        if not admin or not admin.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not admin.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        admin.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = generate_token(admin.id, 'admin', admin.email)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'admin': admin.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-token', methods=['POST'])
@token_required
def verify_token():
    """Verify if token is valid and return user info"""
    try:
        user_info = request.current_user
        
        if user_info['type'] == 'partner':
            partner = Partner.query.get(user_info['id'])
            if not partner or partner.status != PartnerStatus.APPROVED:
                return jsonify({'error': 'Partner not found or not approved'}), 404
            return jsonify({
                'valid': True,
                'user_type': 'partner',
                'user': partner.to_dict()
            }), 200
            
        elif user_info['type'] == 'admin':
            admin = Admin.query.get(user_info['id'])
            if not admin or not admin.is_active:
                return jsonify({'error': 'Admin not found or inactive'}), 404
            return jsonify({
                'valid': True,
                'user_type': 'admin',
                'user': admin.to_dict()
            }), 200
        
        return jsonify({'error': 'Invalid user type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/partner/profile', methods=['GET'])
@token_required
def get_partner_profile():
    """Get partner profile information"""
    try:
        if request.current_user['type'] != 'partner':
            return jsonify({'error': 'Partner access required'}), 403
        
        partner = Partner.query.get(request.current_user['id'])
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        return jsonify({'partner': partner.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/partner/profile', methods=['PUT'])
@token_required
def update_partner_profile():
    """Update partner profile information"""
    try:
        if request.current_user['type'] != 'partner':
            return jsonify({'error': 'Partner access required'}), 403
        
        partner = Partner.query.get(request.current_user['id'])
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        updatable_fields = ['contact_name', 'phone', 'interests']
        for field in updatable_fields:
            if field in data:
                setattr(partner, field, data[field])
        
        partner.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'partner': partner.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        user_info = request.current_user
        
        if user_info['type'] == 'partner':
            user = Partner.query.get(user_info['id'])
        elif user_info['type'] == 'admin':
            user = Admin.query.get(user_info['id'])
        else:
            return jsonify({'error': 'Invalid user type'}), 400
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check current password
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Set new password
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

