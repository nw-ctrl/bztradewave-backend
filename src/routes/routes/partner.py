from flask import Blueprint, request, jsonify
from src.models.partner import db, Partner, Message, Document, MarketInsight, NewsArticle, PartnerStatus
from src.routes.auth import token_required
from datetime import datetime
from sqlalchemy import desc

partner_bp = Blueprint('partner', __name__)

@partner_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def get_partner_dashboard_stats():
    """Get partner dashboard statistics"""
    try:
        if request.current_user['type'] != 'partner':
            return jsonify({'error': 'Partner access required'}), 403
        
        partner_id = request.current_user['id']
        partner = Partner.query.get(partner_id)
        
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        # Mock trade statistics for demo
        stats = {
            'trade_volume': '$2.4M',
            'trade_growth': '+12.5%',
            'active_deals': 24,
            'deals_growth': '+8.2%',
            'global_reach': 15,
            'success_rate': '98.5%'
        }
        
        # Mock trade volume data
        trade_volume_data = [
            {'month': 'Jan', 'volume': 2400},
            {'month': 'Feb', 'volume': 1398},
            {'month': 'Mar', 'volume': 9800},
            {'month': 'Apr', 'volume': 3908},
            {'month': 'May', 'volume': 4800},
            {'month': 'Jun', 'volume': 3800}
        ]
        
        # Mock category distribution
        category_distribution = [
            {'name': 'Agriculture', 'value': 35, 'color': '#10B981'},
            {'name': 'Electronics', 'value': 45, 'color': '#3B82F6'},
            {'name': 'Fashion', 'value': 20, 'color': '#8B5CF6'}
        ]
        
        # Recent activities
        recent_activities = [
            {
                'id': 1,
                'type': 'trade',
                'message': 'New trade opportunity in Electronics sector',
                'time': '2 hours ago'
            },
            {
                'id': 2,
                'type': 'message',
                'message': 'Admin response to your inquiry',
                'time': '4 hours ago'
            },
            {
                'id': 3,
                'type': 'document',
                'message': 'Market report Q4 2025 available',
                'time': '1 day ago'
            },
            {
                'id': 4,
                'type': 'alert',
                'message': 'Price alert: Wheat futures up 5%',
                'time': '2 days ago'
            }
        ]
        
        return jsonify({
            'stats': stats,
            'trade_volume_data': trade_volume_data,
            'category_distribution': category_distribution,
            'recent_activities': recent_activities
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partner_bp.route('/market-insights', methods=['GET'])
@token_required
def get_partner_market_insights():
    """Get AI-powered market insights for partners"""
    try:
        if request.current_user['type'] != 'partner':
            return jsonify({'error': 'Partner access required'}), 403
        
        # Get active market insights
        insights = MarketInsight.query.filter_by(is_active=True).order_by(desc(MarketInsight.created_at)).limit(10).all()
        
        # Mock market trends data
        market_trends_data = [
            {'month': 'Jan', 'agriculture': 4000, 'electronics': 2400, 'fashion': 2400},
            {'month': 'Feb', 'agriculture': 3000, 'electronics': 1398, 'fashion': 2210},
            {'month': 'Mar', 'agriculture': 2000, 'electronics': 9800, 'fashion': 2290},
            {'month': 'Apr', 'agriculture': 2780, 'electronics': 3908, 'fashion': 2000},
            {'month': 'May', 'agriculture': 1890, 'electronics': 4800, 'fashion': 2181},
            {'month': 'Jun', 'agriculture': 2390, 'electronics': 3800, 'fashion': 2500}
        ]
        
        # Mock AI forecasts
        ai_forecasts = {
            'agriculture': {
                'title': 'Agriculture Forecast',
                'confidence': 'High Confidence',
                'description': 'AI predicts 15% growth in agriculture exports to Asia-Pacific region over next quarter.',
                'metrics': [
                    {'name': 'Wheat', 'change': '+18%'},
                    {'name': 'Beef', 'change': '+12%'},
                    {'name': 'Dairy', 'change': '+8%'}
                ]
            },
            'electronics': {
                'title': 'Electronics Trends',
                'confidence': 'Medium Confidence',
                'description': 'Component prices stabilizing after recent volatility. Supply chain improvements expected.',
                'metrics': [
                    {'name': 'Semiconductors', 'change': 'Stable'},
                    {'name': 'Consumer Electronics', 'change': '+5%'},
                    {'name': 'Components', 'change': '-3%'}
                ]
            },
            'fashion': {
                'title': 'Fashion Outlook',
                'confidence': 'High Confidence',
                'description': 'Sustainable fashion showing strong growth. Premium materials in high demand.',
                'metrics': [
                    {'name': 'Organic Cotton', 'change': '+22%'},
                    {'name': 'Wool Products', 'change': '+15%'},
                    {'name': 'Synthetic', 'change': '-8%'}
                ]
            }
        }
        
        return jsonify({
            'insights': [insight.to_dict() for insight in insights],
            'market_trends_data': market_trends_data,
            'ai_forecasts': ai_forecasts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partner_bp.route('/messages', methods=['GET'])
@token_required
def get_partner_messages():
    """Get messages for partner"""
    try:
        if request.current_user['type'] != 'partner':
            return jsonify({'error': 'Partner access required'}), 403
        
        partner_id = request.current_user['id']
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        messages = Message.query.filter_by(partner_id=partner_id).order_by(desc(Message.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Mark messages as read when fetched
        unread_messages = Message.query.filter_by(partner_id=partner_id, is_read=False).all()
        for msg in unread_messages:
            msg.is_read = True
        db.session.commit()
        
        return jsonify({
            'messages': [msg.to_dict() for msg in messages.items],
            'total': messages.total,
            'pages': messages.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partner_bp.route('/messages', methods=['POST'])
@token_required
def send_partner_message():
    """Send message to admin"""
    try:
        if request.current_user['type'] != 'partner':
            return jsonify({'error': 'Partner access required'}), 403
        
        partner_id = request.current_user['id']
        data = request.get_json()
        
        subject = data.get('subject', '')
        content = data.get('content')
        
        if not content:
            return jsonify({'error': 'Message content is required'}), 400
        
        message = Message(
            partner_id=partner_id,
            sender_type='partner',
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

@partner_bp.route('/documents', methods=['GET'])
@token_required
def get_partner_documents():
    """Get documents for partner"""
    try:
        if request.current_user['type'] != 'partner':
            return jsonify({'error': 'Partner access required'}), 403
        
        partner_id = request.current_user['id']
        
        # Get partner-specific documents and shared documents
        documents = Document.query.filter(
            (Document.partner_id == partner_id) | 
            (Document.is_shared == True)
        ).order_by(desc(Document.created_at)).all()
        
        # Mock documents for demo
        mock_documents = [
            {
                'id': 1,
                'filename': 'Q4_2025_Market_Report.pdf',
                'original_filename': 'Q4 2025 Market Report.pdf',
                'file_size': 2457600,  # 2.4 MB
                'mime_type': 'application/pdf',
                'description': 'Quarterly market analysis and trends',
                'is_shared': True,
                'uploaded_by_type': 'admin',
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 2,
                'filename': 'Partnership_Agreement.pdf',
                'original_filename': 'Partnership Agreement.pdf',
                'file_size': 1258291,  # 1.2 MB
                'mime_type': 'application/pdf',
                'description': 'Official partnership terms and conditions',
                'is_shared': False,
                'uploaded_by_type': 'admin',
                'created_at': (datetime.utcnow()).isoformat()
            },
            {
                'id': 3,
                'filename': 'Trade_Guidelines.pdf',
                'original_filename': 'Trade Guidelines.pdf',
                'file_size': 911360,  # 890 KB
                'mime_type': 'application/pdf',
                'description': 'International trade best practices',
                'is_shared': True,
                'uploaded_by_type': 'admin',
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 4,
                'filename': 'Compliance_Checklist.pdf',
                'original_filename': 'Compliance Checklist.pdf',
                'file_size': 665600,  # 650 KB
                'mime_type': 'application/pdf',
                'description': 'Regulatory compliance requirements',
                'is_shared': True,
                'uploaded_by_type': 'admin',
                'created_at': datetime.utcnow().isoformat()
            }
        ]
        
        return jsonify({
            'documents': mock_documents
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partner_bp.route('/notifications', methods=['GET'])
@token_required
def get_partner_notifications():
    """Get notifications for partner"""
    try:
        if request.current_user['type'] != 'partner':
            return jsonify({'error': 'Partner access required'}), 403
        
        # Mock notifications for demo
        notifications = [
            {
                'id': 1,
                'title': 'New Market Opportunity',
                'message': 'Electronics demand surge in European markets',
                'priority': 'high',
                'time': '1 hour ago',
                'is_read': False
            },
            {
                'id': 2,
                'title': 'Document Update',
                'message': 'Q4 market report has been updated',
                'priority': 'medium',
                'time': '3 hours ago',
                'is_read': False
            },
            {
                'id': 3,
                'title': 'Price Alert',
                'message': 'Agriculture commodity prices showing upward trend',
                'priority': 'low',
                'time': '6 hours ago',
                'is_read': True
            }
        ]
        
        return jsonify({
            'notifications': notifications
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partner_bp.route('/news', methods=['GET'])
@token_required
def get_partner_news():
    """Get AI-powered news for partners"""
    try:
        if request.current_user['type'] != 'partner':
            return jsonify({'error': 'Partner access required'}), 403
        
        category = request.args.get('category')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = NewsArticle.query
        
        if category:
            query = query.filter_by(category=category)
        
        news = query.order_by(desc(NewsArticle.published_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Mock news articles for demo
        mock_news = [
            {
                'id': 1,
                'title': 'Global Electronics Trade Reaches Record High in Q4 2025',
                'summary': 'International electronics trade volume increased by 23% compared to the previous quarter, driven by strong demand for semiconductors and consumer electronics.',
                'category': 'electronics',
                'published_at': datetime.utcnow().isoformat(),
                'is_featured': True,
                'image_url': '/api/placeholder/400/200'
            },
            {
                'id': 2,
                'title': 'Australian Agriculture Exports Show Strong Growth',
                'summary': 'Premium agricultural products from Australia continue to gain market share in Asia-Pacific region, with organic certification driving premium pricing.',
                'category': 'agriculture',
                'published_at': datetime.utcnow().isoformat(),
                'is_featured': False,
                'image_url': '/api/placeholder/400/200'
            },
            {
                'id': 3,
                'title': 'Sustainable Fashion Trends Reshape Global Trade',
                'summary': 'Eco-friendly materials and ethical production methods are becoming key differentiators in the international fashion trade market.',
                'category': 'fashion',
                'published_at': datetime.utcnow().isoformat(),
                'is_featured': False,
                'image_url': '/api/placeholder/400/200'
            }
        ]
        
        return jsonify({
            'news': mock_news,
            'total': len(mock_news),
            'pages': 1,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partner_bp.route('/activity-log', methods=['GET'])
@token_required
def get_partner_activity_log():
    """Get partner activity log"""
    try:
        if request.current_user['type'] != 'partner':
            return jsonify({'error': 'Partner access required'}), 403
        
        partner_id = request.current_user['id']
        partner = Partner.query.get(partner_id)
        
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        # Mock activity log
        activity_log = [
            {
                'id': 1,
                'action': 'Login',
                'description': 'Successful login to partner portal',
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': '192.168.1.1'
            },
            {
                'id': 2,
                'action': 'Message Sent',
                'description': 'Sent message to admin team',
                'timestamp': (datetime.utcnow()).isoformat(),
                'ip_address': '192.168.1.1'
            },
            {
                'id': 3,
                'action': 'Document Downloaded',
                'description': 'Downloaded Q4 2025 Market Report',
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': '192.168.1.1'
            }
        ]
        
        return jsonify({
            'activity_log': activity_log,
            'partner_info': {
                'login_count': partner.login_count,
                'last_login': partner.last_login.isoformat() if partner.last_login else None,
                'member_since': partner.created_at.isoformat() if partner.created_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

