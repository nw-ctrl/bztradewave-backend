from flask import Blueprint, request, jsonify
from src.models.partner import db, Partner, Admin, Message, Document, MarketInsight, PartnerStatus
from src.routes.auth import token_required, admin_required
from datetime import datetime
from sqlalchemy import func, desc

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard/stats', methods=['GET'])
@token_required
@admin_required
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        # Partner statistics
        total_partners = Partner.query.filter_by(status=PartnerStatus.APPROVED).count()
        pending_applications = Partner.query.filter_by(status=PartnerStatus.PENDING).count()
        
        # Calculate growth (mock data for demo)
        partner_growth = "+12"
        application_growth = "+3"
        
        # Trade volume (mock data)
        trade_volume = "$17M"
        volume_growth = "+15%"
        
        # Active countries (mock data)
        active_countries = 25
        country_growth = "+2"
        
        stats = {
            'total_partners': total_partners,
            'partner_growth': partner_growth,
            'pending_applications': pending_applications,
            'application_growth': application_growth,
            'trade_volume': trade_volume,
            'volume_growth': volume_growth,
            'active_countries': active_countries,
            'country_growth': country_growth
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/partners/applications', methods=['GET'])
@token_required
@admin_required
def get_partner_applications():
    """Get all partner applications"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status')
        search = request.args.get('search', '')
        
        query = Partner.query
        
        # Apply filters
        if status_filter:
            query = query.filter_by(status=PartnerStatus(status_filter))
        
        if search:
            query = query.filter(
                (Partner.company_name.contains(search)) |
                (Partner.contact_name.contains(search)) |
                (Partner.email.contains(search))
            )
        
        # Order by creation date (newest first)
        query = query.order_by(desc(Partner.created_at))
        
        # Paginate
        partners = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'applications': [partner.to_dict(include_sensitive=True) for partner in partners.items],
            'total': partners.total,
            'pages': partners.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/partners/<int:partner_id>/approve', methods=['POST'])
@token_required
@admin_required
def approve_partner(partner_id):
    """Approve a partner application"""
    try:
        partner = Partner.query.get(partner_id)
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        if partner.status != PartnerStatus.PENDING:
            return jsonify({'error': 'Partner application is not pending'}), 400
        
        # Approve partner
        partner.status = PartnerStatus.APPROVED
        partner.approved_at = datetime.utcnow()
        partner.approved_by = request.current_user['id']
        partner.updated_at = datetime.utcnow()
        
        # Set default password for demo
        if not partner.password_hash:
            partner.set_password('demo123')
        
        db.session.commit()
        
        # Send welcome message (optional)
        welcome_message = Message(
            partner_id=partner.id,
            admin_id=request.current_user['id'],
            sender_type='admin',
            subject='Welcome to bzTradewave.au',
            content='Welcome to the partner portal! We\'re excited to work with you. Please don\'t hesitate to reach out if you have any questions or need assistance.'
        )
        db.session.add(welcome_message)
        db.session.commit()
        
        return jsonify({
            'message': 'Partner approved successfully',
            'partner': partner.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/partners/<int:partner_id>/reject', methods=['POST'])
@token_required
@admin_required
def reject_partner(partner_id):
    """Reject a partner application"""
    try:
        partner = Partner.query.get(partner_id)
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        if partner.status != PartnerStatus.PENDING:
            return jsonify({'error': 'Partner application is not pending'}), 400
        
        data = request.get_json()
        reason = data.get('reason', 'Application does not meet our requirements')
        
        # Reject partner
        partner.status = PartnerStatus.REJECTED
        partner.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send rejection message
        rejection_message = Message(
            partner_id=partner.id,
            admin_id=request.current_user['id'],
            sender_type='admin',
            subject='Partnership Application Update',
            content=f'Thank you for your interest in partnering with bzTradewave.au. Unfortunately, we are unable to approve your application at this time. Reason: {reason}'
        )
        db.session.add(rejection_message)
        db.session.commit()
        
        return jsonify({
            'message': 'Partner application rejected',
            'partner': partner.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/partners/active', methods=['GET'])
@token_required
@admin_required
def get_active_partners():
    """Get all active partners"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Partner.query.filter_by(status=PartnerStatus.APPROVED)
        
        if search:
            query = query.filter(
                (Partner.company_name.contains(search)) |
                (Partner.contact_name.contains(search)) |
                (Partner.email.contains(search))
            )
        
        # Order by last activity (most recent first)
        query = query.order_by(desc(Partner.last_login))
        
        # Paginate
        partners = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'partners': [partner.to_dict() for partner in partners.items],
            'total': partners.total,
            'pages': partners.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/partners/<int:partner_id>', methods=['GET'])
@token_required
@admin_required
def get_partner_details(partner_id):
    """Get detailed partner information"""
    try:
        partner = Partner.query.get(partner_id)
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        # Get partner messages
        messages = Message.query.filter_by(partner_id=partner_id).order_by(desc(Message.created_at)).limit(10).all()
        
        # Get partner documents
        documents = Document.query.filter_by(partner_id=partner_id).order_by(desc(Document.created_at)).limit(10).all()
        
        return jsonify({
            'partner': partner.to_dict(include_sensitive=True),
            'recent_messages': [msg.to_dict() for msg in messages],
            'recent_documents': [doc.to_dict() for doc in documents]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/partners/<int:partner_id>/suspend', methods=['POST'])
@token_required
@admin_required
def suspend_partner(partner_id):
    """Suspend a partner account"""
    try:
        partner = Partner.query.get(partner_id)
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        data = request.get_json()
        reason = data.get('reason', 'Account suspended by admin')
        
        partner.status = PartnerStatus.SUSPENDED
        partner.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send suspension message
        suspension_message = Message(
            partner_id=partner.id,
            admin_id=request.current_user['id'],
            sender_type='admin',
            subject='Account Suspended',
            content=f'Your account has been suspended. Reason: {reason}. Please contact support for more information.'
        )
        db.session.add(suspension_message)
        db.session.commit()
        
        return jsonify({
            'message': 'Partner account suspended',
            'partner': partner.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/messages', methods=['GET'])
@token_required
@admin_required
def get_admin_messages():
    """Get messages for admin"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        partner_id = request.args.get('partner_id', type=int)
        
        query = Message.query
        
        if partner_id:
            query = query.filter_by(partner_id=partner_id)
        
        query = query.order_by(desc(Message.created_at))
        
        messages = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Include partner info with messages
        message_list = []
        for msg in messages.items:
            msg_dict = msg.to_dict()
            if msg.partner:
                msg_dict['partner_name'] = msg.partner.company_name
                msg_dict['partner_email'] = msg.partner.email
            message_list.append(msg_dict)
        
        return jsonify({
            'messages': message_list,
            'total': messages.total,
            'pages': messages.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/messages', methods=['POST'])
@token_required
@admin_required
def send_admin_message():
    """Send message to partner"""
    try:
        data = request.get_json()
        partner_id = data.get('partner_id')
        subject = data.get('subject', '')
        content = data.get('content')
        
        if not partner_id or not content:
            return jsonify({'error': 'Partner ID and content are required'}), 400
        
        # Verify partner exists
        partner = Partner.query.get(partner_id)
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        message = Message(
            partner_id=partner_id,
            admin_id=request.current_user['id'],
            sender_type='admin',
            subject=subject,
            content=content
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_data': message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/market-insights', methods=['GET'])
@token_required
@admin_required
def get_market_insights():
    """Get AI-powered market insights"""
    try:
        category = request.args.get('category')
        
        query = MarketInsight.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        insights = query.order_by(desc(MarketInsight.created_at)).all()
        
        return jsonify({
            'insights': [insight.to_dict() for insight in insights]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/market-insights', methods=['POST'])
@token_required
@admin_required
def create_market_insight():
    """Create new market insight"""
    try:
        data = request.get_json()
        
        required_fields = ['category', 'title', 'content', 'confidence_level']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        insight = MarketInsight(
            category=data['category'],
            title=data['title'],
            content=data['content'],
            confidence_level=data['confidence_level'],
            data_source=data.get('data_source', 'Admin Input')
        )
        
        db.session.add(insight)
        db.session.commit()
        
        return jsonify({
            'message': 'Market insight created successfully',
            'insight': insight.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/customer-activity', methods=['GET'])
@token_required
@admin_required
def get_customer_activity():
    """Get AI-powered customer activity analytics"""
    try:
        # Mock AI-generated customer activity data
        activity_data = {
            'agriculture': {
                'active_customers': 15,
                'high_value_customers': 8,
                'growth_potential': '+18%',
                'risk_level': 'Low',
                'ai_recommendation': 'AI recommends focusing on premium grain exports to Asia-Pacific region.'
            },
            'electronics': {
                'active_customers': 22,
                'high_value_customers': 12,
                'growth_potential': '+12%',
                'risk_level': 'Medium',
                'ai_recommendation': 'Supply chain stabilization creating new opportunities in component trading.'
            },
            'fashion': {
                'active_customers': 18,
                'high_value_customers': 10,
                'growth_potential': '+25%',
                'risk_level': 'Low',
                'ai_recommendation': 'Sustainable fashion trend driving premium pricing and demand growth.'
            }
        }
        
        # Mock real-time alerts
        alerts = [
            {
                'type': 'high_activity',
                'title': 'High Activity Alert',
                'message': 'Electronics sector showing 35% increase in trade inquiries over the past 48 hours. Recommend prioritizing customer outreach in this sector.',
                'priority': 'high',
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'type': 'growth_opportunity',
                'title': 'Growth Opportunity',
                'message': '3 agriculture customers showing expansion signals. AI predicts 40% revenue increase potential with targeted premium product offerings.',
                'priority': 'medium',
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'type': 'attention_required',
                'title': 'Attention Required',
                'message': '2 fashion sector customers showing decreased activity. Recommend proactive engagement to maintain relationship strength.',
                'priority': 'low',
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        
        return jsonify({
            'customer_activity': activity_data,
            'ai_alerts': alerts,
            'last_updated': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/trade-volume', methods=['GET'])
@token_required
@admin_required
def get_trade_volume_analytics():
    """Get trade volume analytics"""
    try:
        # Mock trade volume data
        monthly_data = [
            {'month': 'Jan', 'volume': 12000},
            {'month': 'Feb', 'volume': 15000},
            {'month': 'Mar', 'volume': 18000},
            {'month': 'Apr', 'volume': 16000},
            {'month': 'May', 'volume': 20000},
            {'month': 'Jun', 'volume': 22000}
        ]
        
        # Regional distribution
        regional_data = [
            {'name': 'Asia-Pacific', 'value': 45, 'color': '#3B82F6'},
            {'name': 'Europe', 'value': 30, 'color': '#10B981'},
            {'name': 'North America', 'value': 15, 'color': '#F59E0B'},
            {'name': 'Others', 'value': 10, 'color': '#8B5CF6'}
        ]
        
        return jsonify({
            'monthly_volume': monthly_data,
            'regional_distribution': regional_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

