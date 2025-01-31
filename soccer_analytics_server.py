import os
import sys
import threading
import subprocess
import time
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.FileHandler('/Users/niladridas/Documents/ml-soccer/server_logs.txt'),
                        logging.StreamHandler(sys.stdout)
                    ])
logger = logging.getLogger(__name__)

# Import our custom modules
sys.path.append('/Users/niladridas/Documents/ml-soccer')

def generate_player_data():
    """Wrapper function for data generation"""
    import pandas as pd
    import numpy as np
    import random

    # Set random seed for reproducibility
    np.random.seed(42)

    # Top 4 teams
    top_teams = [
        'Manchester City', 
        'Arsenal', 
        'Manchester United', 
        'Liverpool'
    ]

    # Detailed player names for each team
    team_players = {
        'Manchester City': [
            'Erling Haaland', 'Kevin De Bruyne', 'Rodri', 'Phil Foden', 
            'Jack Grealish', 'Bernardo Silva', 'Ruben Dias', 'John Stones', 
            'Kyle Walker', 'Ederson', 'Julian Alvarez', 'Rico Lewis'
        ],
        'Arsenal': [
            'Bukayo Saka', 'Martin Odegaard', 'Gabriel Jesus', 'Gabriel Martinelli', 
            'William Saliba', 'Declan Rice', 'Aaron Ramsdale', 'Gabriel Magalhaes', 
            'Ben White', 'Oleksandr Zinchenko', 'Kai Havertz', 'Eddie Nketiah'
        ],
        'Manchester United': [
            'Bruno Fernandes', 'Marcus Rashford', 'Rasmus Hojlund', 'Mason Mount', 
            'Lisandro Martinez', 'Harry Maguire', 'Raphael Varane', 'Casemiro', 
            'Scott McTominay', 'David de Gea', 'Antony', 'Luke Shaw'
        ],
        'Liverpool': [
            'Mohamed Salah', 'Virgil van Dijk', 'Alisson', 'Trent Alexander-Arnold', 
            'Andy Robertson', 'Darwin Nunez', 'Cody Gakpo', 'Luis Diaz', 
            'Dominik Szoboszlai', 'Wataru Endo', 'Joel Matip', 'Ibrahima Konate'
        ]
    }

    # Generate player data
    all_players = []
    for team in top_teams:
        team_player_names = team_players[team]
        
        for player_name in team_player_names:
            # Determine position based on known player
            if any(name in player_name for name in ['Goalkeeper', 'Alisson', 'Ederson', 'de Gea', 'Ramsdale']):
                position = 'Goalkeeper'
            elif any(name in player_name for name in ['van Dijk', 'Dias', 'Saliba', 'Maguire', 'Martinez', 'Varane']):
                position = 'Defender'
            elif any(name in player_name for name in ['De Bruyne', 'Fernandes', 'Odegaard', 'Saka', 'Rice', 'Casemiro']):
                position = 'Midfielder'
            else:
                position = 'Forward'
            
            # Generate player
            player = {
                'Player_Name': player_name,
                'Club': team,
                'Position': position,
                'Goals': random.randint(5, 30),
                'Assists': random.randint(3, 20),
                'Passes_Completed': random.randint(100, 700),
                'Pass_Accuracy': random.uniform(70, 95),
                'Shot_Accuracy': random.uniform(50, 90),
                'Tackles_Won': random.randint(10, 200)
            }
            
            all_players.append(player)

    # Create DataFrame
    df = pd.DataFrame(all_players)

    # Ensure data directory exists
    os.makedirs('/Users/niladridas/Documents/ml-soccer/data', exist_ok=True)

    # Save to CSV
    df.to_csv('/Users/niladridas/Documents/ml-soccer/data/player_stats.csv', index=False)

    print(f"Generated dataset with {len(df)} players across {len(top_teams)} top teams")
    return df

from advanced_soccer_math import SoccerMathAnalytics
from player_recommendation_system import PlayerRecommendationSystem

class SoccerAnalyticsServer:
    def __init__(self, port=5001):
        """
        Initialize the Soccer Analytics Server
        
        Args:
            port (int): Port number to run the server on. Defaults to 5001.
        """
        self.port = port
        self.app = Flask(__name__, 
                         static_folder='static', 
                         template_folder='templates')
        
        # Enable CORS
        CORS(self.app)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Generate initial dataset
        self.player_data = generate_player_data()
        
        # Setup routes
        self._setup_routes()
        
        # Initialize math analytics
        self.math_analytics = SoccerMathAnalytics(self.player_data)
        
        # Initialize recommendation system
        self.recommendation_system = PlayerRecommendationSystem(self.player_data)
        
        self.logger.info(f"🚀 Soccer Analytics Server initialized on port {self.port}")
    
    def _setup_routes(self):
        """Setup all API routes for the server"""
        @self.app.route('/')
        def index():
            """Main landing page"""
            return render_template('index.html')
        
        @self.app.route('/analytics_dashboard')
        def analytics_dashboard():
            """Analytics dashboard route"""
            return render_template('analytics_dashboard.html')
        
        @self.app.route('/regenerate_data', methods=['POST'])
        def regenerate_data():
            """Endpoint to regenerate player data"""
            try:
                # Regenerate data
                self.player_data = generate_player_data()
                
                # Recompute analytics
                self.math_analytics = SoccerMathAnalytics(self.player_data)
                
                return jsonify({
                    'status': 'success', 
                    'message': 'Data regenerated successfully',
                    'timestamp': time.time()
                }), 200
            except Exception as e:
                logger.error(f"Data regeneration failed: {e}")
                return jsonify({
                    'status': 'error', 
                    'message': str(e)
                }), 500
        
        @self.app.route('/team_performance_analysis')
        def team_performance_analysis():
            """Provide comprehensive team performance analysis"""
            try:
                team_analysis = self.math_analytics.team_performance_analysis()
                performance_dist = self.math_analytics.player_performance_distribution()
                correlations = self.math_analytics.correlation_matrix()
                predictive_rating = self.math_analytics.predictive_player_rating()
                
                return jsonify({
                    'team_performance': team_analysis.to_dict(),
                    'performance_distribution': performance_dist['overall_stats'].to_dict(),
                    'correlations': {
                        'pearson': correlations['pearson_correlation'].to_dict(),
                        'spearman': correlations['spearman_correlation'].to_dict()
                    },
                    'predictive_rating': {
                        'feature_importance': predictive_rating['feature_importance'].to_dict(),
                        'model_score': predictive_rating['model_score']
                    }
                }), 200
            except Exception as e:
                logger.error(f"Performance analysis failed: {e}")
                return jsonify({
                    'status': 'error', 
                    'message': str(e)
                }), 500
        
        @self.app.route('/recommend_players', methods=['POST'])
        def recommend_players():
            """Advanced player recommendation endpoint"""
            try:
                data = request.get_json()
                player_name = data.get('player_name')
                recommendation_type = data.get('type', 'similar')
                
                rec_system = PlayerRecommendationSystem(self.player_data)
                
                if recommendation_type == 'similar':
                    recommendations = rec_system.find_similar_players(player_name)
                elif recommendation_type == 'position':
                    position = data.get('position', 'Forward')
                    recommendations = rec_system.position_based_recommendations(position)
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid recommendation type'
                    }), 400
                
                return jsonify({
                    'status': 'success',
                    'recommendations': recommendations.to_dict(orient='records')
                }), 200
            
            except Exception as e:
                logger.error(f"Player recommendation failed: {e}")
                return jsonify({
                    'status': 'error', 
                    'message': str(e)
                }), 500
        
        @self.app.route('/player_insights')
        def player_insights():
            """Comprehensive player performance insights"""
            try:
                rec_system = PlayerRecommendationSystem(self.player_data)
                insights = rec_system.generate_player_insights()
                
                return jsonify({
                    'status': 'success',
                    'insights': insights
                }), 200
            
            except Exception as e:
                logger.error(f"Player insights generation failed: {e}")
                return jsonify({
                    'status': 'error', 
                    'message': str(e)
                }), 500
        
        @self.app.route('/predict_player_performance', methods=['POST'])
        def predict_player_performance():
            """Predict player performance based on input features"""
            try:
                data = request.get_json()
                features = data.get('features')
                
                if not features:
                    return jsonify({
                        'status': 'error',
                        'message': 'No features provided'
                    }), 400
                
                rec_system = PlayerRecommendationSystem(self.player_data)
                prediction = rec_system.predict_player_performance(features)
                
                return jsonify({
                    'status': 'success',
                    'predicted_performance': prediction.tolist()
                }), 200
            
            except Exception as e:
                logger.error(f"Player performance prediction failed: {e}")
                return jsonify({
                    'status': 'error', 
                    'message': str(e)
                }), 500

    def run(self, debug=True):
        """
        Run the Soccer Analytics Server
        
        Args:
            debug (bool): Enable debug mode. Defaults to True.
        """
        self.logger.info(f"🚀 Starting Soccer Analytics Server on 0.0.0.0:{self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)

# Main execution
if __name__ == '__main__':
    server = SoccerAnalyticsServer(port=5001)
    server.run()
