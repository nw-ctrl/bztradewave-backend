import google.generativeai as genai
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class GeminiAIService:
    def __init__(self):
        # Configure Gemini AI
        api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def generate_market_insights(self, industry: str = "general") -> Dict:
        """Generate AI-powered market insights for specific industries"""
        try:
            prompt = f"""
            As an expert market analyst for bzTradewave.au, generate comprehensive market insights for the {industry} industry.
            
            Please provide:
            1. Current market trends (3-4 key trends)
            2. Price analysis and predictions
            3. Supply and demand factors
            4. Regional market differences (Asia, Europe, Australia)
            5. Risk factors and opportunities
            6. Actionable recommendations for traders
            
            Focus on Australian import/export perspective and international trade opportunities.
            Format the response as a structured analysis that would be valuable for business decision-making.
            Keep it professional and data-driven.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "industry": industry,
                "insights": response.text,
                "generated_at": datetime.now().isoformat(),
                "source": "Gemini AI Analysis"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate market insights: {str(e)}",
                "industry": industry,
                "generated_at": datetime.now().isoformat()
            }
    
    def generate_trade_news(self, count: int = 5) -> List[Dict]:
        """Generate AI-powered trade news articles"""
        try:
            prompt = f"""
            As a trade news analyst for bzTradewave.au, generate {count} realistic and current trade news headlines and summaries.
            
            Focus on:
            - Australian import/export developments
            - Global trade trends affecting agriculture, electronics, and fashion
            - Market opportunities and challenges
            - Regional trade agreements and policies
            - Supply chain developments
            
            For each news item, provide:
            1. Compelling headline
            2. Brief summary (2-3 sentences)
            3. Industry category (Agriculture, Electronics, Fashion, or General)
            4. Impact level (High, Medium, Low)
            5. Relevance to Australian traders
            
            Format as JSON array with objects containing: headline, summary, category, impact, relevance
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse as JSON, fallback to structured text
            try:
                news_data = json.loads(response.text)
                if isinstance(news_data, list):
                    return news_data
            except:
                pass
            
            # Fallback: parse structured text response
            news_items = []
            lines = response.text.split('\n')
            current_item = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
                    if current_item:
                        news_items.append(current_item)
                    current_item = {
                        "headline": line[2:].strip(),
                        "summary": "AI-generated trade news analysis",
                        "category": "General",
                        "impact": "Medium",
                        "relevance": "High for Australian traders",
                        "generated_at": datetime.now().isoformat()
                    }
            
            if current_item:
                news_items.append(current_item)
                
            return news_items[:count]
            
        except Exception as e:
            return [{
                "headline": "AI Service Temporarily Unavailable",
                "summary": f"Unable to generate trade news: {str(e)}",
                "category": "System",
                "impact": "Low",
                "relevance": "System notification",
                "generated_at": datetime.now().isoformat()
            }]
    
    def analyze_partner_data(self, partner_info: Dict) -> Dict:
        """Analyze partner data and provide AI insights"""
        try:
            prompt = f"""
            As a business analyst for bzTradewave.au, analyze this partner profile and provide insights:
            
            Partner Information:
            - Company: {partner_info.get('company', 'Unknown')}
            - Country: {partner_info.get('country', 'Unknown')}
            - Business Type: {partner_info.get('business_type', 'Unknown')}
            - Revenue Range: {partner_info.get('revenue', 'Unknown')}
            
            Provide:
            1. Partnership potential score (1-10)
            2. Key strengths and opportunities
            3. Potential risks or concerns
            4. Recommended engagement strategy
            5. Market compatibility assessment
            
            Keep analysis professional and actionable for business development.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "partner_analysis": response.text,
                "analyzed_at": datetime.now().isoformat(),
                "partner_company": partner_info.get('company', 'Unknown')
            }
            
        except Exception as e:
            return {
                "error": f"Failed to analyze partner data: {str(e)}",
                "analyzed_at": datetime.now().isoformat()
            }
    
    def generate_customer_insights(self, customer_data: List[Dict]) -> Dict:
        """Generate AI insights about customer behavior and trends"""
        try:
            # Summarize customer data for AI analysis
            total_customers = len(customer_data)
            industries = {}
            countries = {}
            
            for customer in customer_data:
                industry = customer.get('industry', 'Unknown')
                country = customer.get('country', 'Unknown')
                industries[industry] = industries.get(industry, 0) + 1
                countries[country] = countries.get(country, 0) + 1
            
            prompt = f"""
            As a customer analytics expert for bzTradewave.au, analyze this customer data and provide insights:
            
            Customer Overview:
            - Total Active Customers: {total_customers}
            - Top Industries: {dict(sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5])}
            - Top Countries: {dict(sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5])}
            
            Provide:
            1. Customer behavior patterns
            2. Market penetration analysis
            3. Growth opportunities by region/industry
            4. Customer retention strategies
            5. Expansion recommendations
            
            Focus on actionable business intelligence for trade platform optimization.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "customer_insights": response.text,
                "total_customers": total_customers,
                "top_industries": dict(sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]),
                "top_countries": dict(sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate customer insights: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }
    
    def generate_trade_recommendations(self, user_profile: Dict) -> Dict:
        """Generate personalized trade recommendations"""
        try:
            prompt = f"""
            As a trade advisor for bzTradewave.au, provide personalized recommendations for this user:
            
            User Profile:
            - Industry Focus: {user_profile.get('industry', 'General')}
            - Experience Level: {user_profile.get('experience', 'Intermediate')}
            - Geographic Interest: {user_profile.get('regions', 'Global')}
            - Business Size: {user_profile.get('business_size', 'Medium')}
            
            Provide:
            1. Top 3 trade opportunities
            2. Market entry strategies
            3. Risk mitigation advice
            4. Recommended partners or regions
            5. Next steps and action items
            
            Make recommendations specific, actionable, and tailored to their profile.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "recommendations": response.text,
                "user_industry": user_profile.get('industry', 'General'),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate recommendations: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }

