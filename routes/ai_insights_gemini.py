from flask import Blueprint, jsonify, request
import requests
import json
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.gemini_ai import GeminiAIService

ai_insights_gemini_bp = Blueprint('ai_insights_gemini', __name__)

# Initialize Gemini AI service
gemini_service = GeminiAIService()

@ai_insights_gemini_bp.route('/market-insights', methods=['GET'])
def get_market_insights():
    """Get AI-powered market insights"""
    try:
        industry = request.args.get('industry', 'general')
        insights = gemini_service.generate_market_insights(industry)
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch market insights: {str(e)}"}), 500

@ai_insights_gemini_bp.route('/trade-news', methods=['GET'])
def get_trade_news():
    """Get AI-generated trade news"""
    try:
        count = int(request.args.get('count', 5))
        news = gemini_service.generate_trade_news(count)
        return jsonify({"news": news}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch trade news: {str(e)}"}), 500

@ai_insights_gemini_bp.route('/partner-analysis', methods=['POST'])
def analyze_partner():
    """Analyze partner data with AI"""
    try:
        partner_data = request.get_json()
        if not partner_data:
            return jsonify({"error": "No partner data provided"}), 400
        
        analysis = gemini_service.analyze_partner_data(partner_data)
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({"error": f"Failed to analyze partner: {str(e)}"}), 500

@ai_insights_gemini_bp.route('/customer-insights', methods=['GET'])
def get_customer_insights():
    """Get AI-powered customer insights"""
    try:
        # Mock customer data for demonstration
        mock_customers = [
            {"industry": "Agriculture", "country": "Australia", "revenue": "5M-10M"},
            {"industry": "Electronics", "country": "Singapore", "revenue": "10M-50M"},
            {"industry": "Fashion", "country": "China", "revenue": "1M-5M"},
            {"industry": "Agriculture", "country": "New Zealand", "revenue": "5M-10M"},
            {"industry": "Electronics", "country": "Japan", "revenue": "50M+"},
            {"industry": "Fashion", "country": "Italy", "revenue": "10M-50M"},
            {"industry": "Agriculture", "country": "Canada", "revenue": "5M-10M"},
            {"industry": "Electronics", "country": "South Korea", "revenue": "10M-50M"},
        ]
        
        insights = gemini_service.generate_customer_insights(mock_customers)
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({"error": f"Failed to generate customer insights: {str(e)}"}), 500

@ai_insights_gemini_bp.route('/trade-recommendations', methods=['POST'])
def get_trade_recommendations():
    """Get personalized trade recommendations"""
    try:
        user_profile = request.get_json()
        if not user_profile:
            # Default profile
            user_profile = {
                "industry": "General",
                "experience": "Intermediate",
                "regions": "Asia-Pacific",
                "business_size": "Medium"
            }
        
        recommendations = gemini_service.generate_trade_recommendations(user_profile)
        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({"error": f"Failed to generate recommendations: {str(e)}"}), 500

@ai_insights_gemini_bp.route('/ai-status', methods=['GET'])
def get_ai_status():
    """Check AI service status"""
    try:
        # Test AI service with a simple request
        test_insights = gemini_service.generate_market_insights("test")
        
        if "error" in test_insights:
            return jsonify({
                "status": "error",
                "message": "AI service unavailable",
                "details": test_insights.get("error")
            }), 503
        
        return jsonify({
            "status": "operational",
            "message": "Gemini AI service is running",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"AI service check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 503

