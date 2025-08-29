from flask import Blueprint, request, jsonify
from src.models.partner import db, NewsArticle, MarketInsight
from datetime import datetime
from sqlalchemy import desc

public_bp = Blueprint('public', __name__)

@public_bp.route('/contact', methods=['POST'])
def submit_contact_form():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # For demo purposes, we'll just return success
        # In a real application, you would save to database or send email
        
        contact_data = {
            'name': data['name'],
            'email': data['email'],
            'company': data.get('company', ''),
            'phone': data.get('phone', ''),
            'subject': data.get('subject', ''),
            'message': data['message'],
            'submitted_at': datetime.utcnow().isoformat()
        }
        
        # Here you would typically:
        # 1. Save to database
        # 2. Send email notification to admin
        # 3. Send confirmation email to user
        
        return jsonify({
            'message': 'Thank you for your message! We will get back to you within 24 hours.',
            'contact_id': 'demo_' + str(datetime.utcnow().timestamp())
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_bp.route('/news', methods=['GET'])
def get_public_news():
    """Get public news articles"""
    try:
        category = request.args.get('category')
        featured_only = request.args.get('featured', 'false').lower() == 'true'
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Mock news articles for demo
        mock_news = [
            {
                'id': 1,
                'title': 'AI-Powered Trade Analytics Revolutionize International Commerce',
                'summary': 'Advanced artificial intelligence is transforming how businesses analyze market trends and make trade decisions, leading to more efficient and profitable international commerce.',
                'content': 'The integration of artificial intelligence in international trade has reached a new milestone...',
                'category': 'technology',
                'source_url': 'https://example.com/news/ai-trade-analytics',
                'image_url': '/api/placeholder/600/300',
                'published_at': datetime.utcnow().isoformat(),
                'is_featured': True
            },
            {
                'id': 2,
                'title': 'Australian Agriculture Exports Reach New Heights',
                'summary': 'Australia\'s agricultural sector continues to expand its global footprint with record-breaking export volumes in key commodities including wheat, beef, and dairy products.',
                'content': 'The Australian agricultural industry has achieved unprecedented success...',
                'category': 'agriculture',
                'source_url': 'https://example.com/news/australia-agriculture-exports',
                'image_url': '/api/placeholder/600/300',
                'published_at': (datetime.utcnow()).isoformat(),
                'is_featured': True
            },
            {
                'id': 3,
                'title': 'Electronics Supply Chain Stabilization Boosts Global Trade',
                'summary': 'Recent improvements in global electronics supply chains are creating new opportunities for international traders and manufacturers worldwide.',
                'content': 'The electronics industry has seen significant stabilization...',
                'category': 'electronics',
                'source_url': 'https://example.com/news/electronics-supply-chain',
                'image_url': '/api/placeholder/600/300',
                'published_at': datetime.utcnow().isoformat(),
                'is_featured': False
            },
            {
                'id': 4,
                'title': 'Sustainable Fashion Drives Premium Market Growth',
                'summary': 'Eco-conscious consumers are driving demand for sustainable fashion products, creating lucrative opportunities for ethical manufacturers and traders.',
                'content': 'The sustainable fashion movement has gained significant momentum...',
                'category': 'fashion',
                'source_url': 'https://example.com/news/sustainable-fashion-growth',
                'image_url': '/api/placeholder/600/300',
                'published_at': datetime.utcnow().isoformat(),
                'is_featured': False
            },
            {
                'id': 5,
                'title': 'Asia-Pacific Trade Partnerships Strengthen Economic Ties',
                'summary': 'New trade agreements and partnerships across the Asia-Pacific region are fostering stronger economic relationships and increased trade volumes.',
                'content': 'The Asia-Pacific region continues to be a hub for international trade...',
                'category': 'trade',
                'source_url': 'https://example.com/news/asia-pacific-partnerships',
                'image_url': '/api/placeholder/600/300',
                'published_at': datetime.utcnow().isoformat(),
                'is_featured': False
            },
            {
                'id': 6,
                'title': 'Digital Transformation Accelerates Global Commerce',
                'summary': 'Digital technologies are streamlining international trade processes, reducing costs and improving efficiency for businesses of all sizes.',
                'content': 'The digital transformation of international trade has accelerated...',
                'category': 'technology',
                'source_url': 'https://example.com/news/digital-transformation-commerce',
                'image_url': '/api/placeholder/600/300',
                'published_at': datetime.utcnow().isoformat(),
                'is_featured': False
            }
        ]
        
        # Filter by category if specified
        if category:
            mock_news = [article for article in mock_news if article['category'] == category]
        
        # Filter by featured if specified
        if featured_only:
            mock_news = [article for article in mock_news if article['is_featured']]
        
        # Simple pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_news = mock_news[start_idx:end_idx]
        
        return jsonify({
            'news': paginated_news,
            'total': len(mock_news),
            'pages': (len(mock_news) + per_page - 1) // per_page,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_bp.route('/news/<int:news_id>', methods=['GET'])
def get_news_article(news_id):
    """Get specific news article"""
    try:
        # Mock news article detail
        mock_article = {
            'id': news_id,
            'title': 'AI-Powered Trade Analytics Revolutionize International Commerce',
            'summary': 'Advanced artificial intelligence is transforming how businesses analyze market trends and make trade decisions, leading to more efficient and profitable international commerce.',
            'content': '''
            <p>The integration of artificial intelligence in international trade has reached a new milestone, with businesses across the globe adopting AI-powered analytics to enhance their trading strategies and market insights.</p>
            
            <p>Recent studies show that companies utilizing AI-driven trade analytics have seen an average increase of 23% in trade efficiency and a 15% improvement in profit margins. These technologies are particularly beneficial for small to medium-sized enterprises that previously lacked access to sophisticated market analysis tools.</p>
            
            <h3>Key Benefits of AI in Trade</h3>
            <ul>
                <li>Real-time market trend analysis</li>
                <li>Predictive pricing models</li>
                <li>Risk assessment and mitigation</li>
                <li>Supply chain optimization</li>
                <li>Automated compliance monitoring</li>
            </ul>
            
            <p>Industry experts predict that AI adoption in international trade will continue to accelerate, with an estimated 80% of trading companies expected to implement some form of AI analytics by 2026.</p>
            
            <p>"AI is not just changing how we trade; it's revolutionizing our understanding of global markets," says Dr. Sarah Chen, Director of Trade Analytics at the International Commerce Institute.</p>
            ''',
            'category': 'technology',
            'source_url': 'https://example.com/news/ai-trade-analytics',
            'image_url': '/api/placeholder/800/400',
            'published_at': datetime.utcnow().isoformat(),
            'is_featured': True,
            'author': 'bzTradewave Research Team',
            'tags': ['AI', 'Technology', 'Trade Analytics', 'International Commerce']
        }
        
        return jsonify({'article': mock_article}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_bp.route('/market-insights/public', methods=['GET'])
def get_public_market_insights():
    """Get public market insights (limited version)"""
    try:
        category = request.args.get('category')
        
        # Mock public market insights (limited compared to partner version)
        mock_insights = [
            {
                'id': 1,
                'category': 'agriculture',
                'title': 'Agriculture Market Outlook',
                'content': 'Global agriculture markets showing positive trends with increased demand for organic and sustainable products.',
                'confidence_level': 'high',
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 2,
                'category': 'electronics',
                'title': 'Electronics Trade Trends',
                'content': 'Electronics sector experiencing stabilization after recent supply chain disruptions, with new opportunities emerging.',
                'confidence_level': 'medium',
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 3,
                'category': 'fashion',
                'title': 'Fashion Industry Evolution',
                'content': 'Sustainable fashion continues to drive market growth with premium pricing for eco-friendly materials.',
                'confidence_level': 'high',
                'created_at': datetime.utcnow().isoformat()
            }
        ]
        
        # Filter by category if specified
        if category:
            mock_insights = [insight for insight in mock_insights if insight['category'] == category]
        
        return jsonify({
            'insights': mock_insights,
            'note': 'Sign up as a partner to access detailed AI-powered market insights and predictions.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_bp.route('/company-stats', methods=['GET'])
def get_company_stats():
    """Get public company statistics"""
    try:
        stats = {
            'total_partners': 150,
            'countries_served': 25,
            'trade_volume': '$17M+',
            'satisfaction_rate': '99.8%',
            'years_experience': 8,
            'active_deals': 240
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_bp.route('/products', methods=['GET'])
def get_products():
    """Get product information"""
    try:
        products = {
            'agriculture': {
                'title': 'Agriculture',
                'description': 'Premium agricultural products from Australia with organic certification and sustainable farming practices.',
                'growth': '+12%',
                'features': [
                    'Organic Certification',
                    'Quality Assurance',
                    'Global Distribution',
                    'Sustainable Practices'
                ],
                'categories': [
                    'Wheat & Grains',
                    'Beef & Livestock',
                    'Dairy Products',
                    'Organic Produce'
                ]
            },
            'electronics': {
                'title': 'Electronics',
                'description': 'Cutting-edge technology solutions and electronic components with comprehensive technical support.',
                'growth': '+8%',
                'features': [
                    'Latest Technology',
                    'Technical Support',
                    'Bulk Orders',
                    'Innovation Partners'
                ],
                'categories': [
                    'Semiconductors',
                    'Consumer Electronics',
                    'Industrial Components',
                    'Smart Devices'
                ]
            },
            'fashion': {
                'title': 'Fashion',
                'description': 'Fashion-forward clothing and garments with sustainable materials and ethical production methods.',
                'growth': '+15%',
                'features': [
                    'Sustainable Materials',
                    'Ethical Production',
                    'Custom Orders',
                    'Fashion Trends'
                ],
                'categories': [
                    'Organic Cotton',
                    'Wool Products',
                    'Sustainable Textiles',
                    'Fashion Accessories'
                ]
            }
        }
        
        return jsonify({'products': products}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

