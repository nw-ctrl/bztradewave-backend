// AI Service for connecting to Gemini AI backend
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://bztradwave-api.onrender.com' 
  : 'http://localhost:5000';

class AIService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/api/gemini`;
  }

  async fetchWithErrorHandling(url, options = {}) {
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('AI Service Error:', error);
      throw error;
    }
  }

  async getMarketInsights(industry = 'general') {
    try {
      const url = `${this.baseURL}/market-insights?industry=${encodeURIComponent(industry)}`;
      return await this.fetchWithErrorHandling(url);
    } catch (error) {
      return {
        error: 'Failed to fetch market insights',
        industry,
        insights: 'AI service temporarily unavailable. Please try again later.',
        generated_at: new Date().toISOString(),
        source: 'Error Handler'
      };
    }
  }

  async getTradeNews(count = 5) {
    try {
      const url = `${this.baseURL}/trade-news?count=${count}`;
      return await this.fetchWithErrorHandling(url);
    } catch (error) {
      return {
        news: [
          {
            headline: 'AI Service Temporarily Unavailable',
            summary: 'Unable to fetch latest trade news. Please check back later.',
            category: 'System',
            impact: 'Low',
            relevance: 'System notification',
            generated_at: new Date().toISOString()
          }
        ]
      };
    }
  }

  async analyzePartner(partnerData) {
    try {
      const url = `${this.baseURL}/partner-analysis`;
      return await this.fetchWithErrorHandling(url, {
        method: 'POST',
        body: JSON.stringify(partnerData),
      });
    } catch (error) {
      return {
        error: 'Failed to analyze partner data',
        partner_analysis: 'AI analysis temporarily unavailable.',
        analyzed_at: new Date().toISOString()
      };
    }
  }

  async getCustomerInsights() {
    try {
      const url = `${this.baseURL}/customer-insights`;
      return await this.fetchWithErrorHandling(url);
    } catch (error) {
      return {
        error: 'Failed to fetch customer insights',
        customer_insights: 'AI insights temporarily unavailable.',
        generated_at: new Date().toISOString()
      };
    }
  }

  async getTradeRecommendations(userProfile = {}) {
    try {
      const url = `${this.baseURL}/trade-recommendations`;
      return await this.fetchWithErrorHandling(url, {
        method: 'POST',
        body: JSON.stringify(userProfile),
      });
    } catch (error) {
      return {
        error: 'Failed to generate recommendations',
        recommendations: 'AI recommendations temporarily unavailable.',
        generated_at: new Date().toISOString()
      };
    }
  }

  async checkAIStatus() {
    try {
      const url = `${this.baseURL}/ai-status`;
      return await this.fetchWithErrorHandling(url);
    } catch (error) {
      return {
        status: 'error',
        message: 'Unable to connect to AI service',
        timestamp: new Date().toISOString()
      };
    }
  }

  // Utility method to format AI responses for display
  formatInsightsForDisplay(insights) {
    if (insights.error) {
      return {
        title: 'AI Service Notice',
        content: insights.insights || insights.error,
        isError: true,
        timestamp: insights.generated_at
      };
    }

    return {
      title: `Market Insights - ${insights.industry}`,
      content: insights.insights,
      isError: false,
      timestamp: insights.generated_at,
      source: insights.source
    };
  }

  formatNewsForDisplay(newsResponse) {
    if (newsResponse.error || !newsResponse.news) {
      return [{
        id: 'error-1',
        title: 'AI News Service Notice',
        summary: newsResponse.error || 'Unable to fetch AI-generated news',
        category: 'system',
        isError: true,
        generated_at: new Date().toISOString()
      }];
    }

    return newsResponse.news.map((item, index) => ({
      id: `ai-news-${index}`,
      title: item.headline,
      summary: item.summary,
      category: item.category?.toLowerCase() || 'general',
      impact: item.impact || 'Medium',
      relevance: item.relevance || 'High',
      isAiGenerated: true,
      generated_at: item.generated_at || new Date().toISOString()
    }));
  }
}

export default new AIService();

