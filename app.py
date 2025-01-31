from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Ensure data directory exists
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

def load_data():
    """Load player statistics from CSV file"""
    try:
        csv_path = os.path.join('data', 'player_stats.csv')
        if not os.path.exists(csv_path):
            logger.error(f"Data file not found: {csv_path}")
            return None
        
        df = pd.read_csv(csv_path)
        logger.info(f"Successfully loaded {len(df)} players from data file")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return None

# Initialize model and scaler
model = None
scaler = None
feature_columns = ['Goals', 'Assists', 'Passes_Completed', 'Pass_Accuracy', 'Shot_Accuracy', 'Tackles_Won']

def init_model():
    """Initialize and train the ML model"""
    global model, scaler
    try:
        model_path = os.path.join('models', 'model.joblib')
        scaler_path = os.path.join('models', 'scaler.joblib')
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            logger.info("Loaded existing model and scaler")
        else:
            logger.info("Training new model...")
            df = load_data()
            if df is not None:
                # Prepare features and target
                X = df[feature_columns]
                y = df['Rating']
                
                # Initialize and fit scaler
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Train model
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_scaled, y)
                
                # Save model and scaler
                joblib.dump(model, model_path)
                joblib.dump(scaler, scaler_path)
                logger.info("Model trained and saved successfully")
            else:
                logger.error("Could not train model: no data available")
    except Exception as e:
        logger.error(f"Error initializing model: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/players')
def get_players():
    try:
        club = request.args.get('club')
        logger.info(f"Getting players with club filter: {club}")
        
        df = load_data()
        if df is None:
            return jsonify({'error': 'Could not load player data'}), 500
        
        if club and club.lower() != 'all':
            df = df[df['Club'] == club]
        
        players = df.to_dict('records')
        logger.info(f"Returning {len(players)} players")
        return jsonify(players)
    except Exception as e:
        logger.error(f"Error in get_players: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/team-stats/<team>')
def get_team_stats(team):
    try:
        logger.info(f"Getting team stats for: {team}")
        df = load_data()
        if df is None:
            return jsonify({'error': 'Could not load player data'}), 500
        
        team_df = df[df['Club'] == team]
        if team_df.empty:
            return jsonify({'error': 'Team not found'}), 404
        
        # Calculate team statistics
        team_stats = {
            'average_rating': round(float(team_df['Rating'].mean()), 1),
            'total_goals': int(team_df['Goals'].sum()),
            'total_assists': int(team_df['Assists'].sum()),
            'avg_pass_accuracy': round(float(team_df['Pass_Accuracy'].mean()), 1),
            'avg_shot_accuracy': round(float(team_df['Shot_Accuracy'].mean()), 1),
            'total_tackles': int(team_df['Tackles_Won'].sum()),
            'player_count': len(team_df),
            'top_scorer': {
                'name': team_df.loc[team_df['Goals'].idxmax(), 'Player_Name'],
                'goals': int(team_df['Goals'].max())
            },
            'top_assister': {
                'name': team_df.loc[team_df['Assists'].idxmax(), 'Player_Name'],
                'assists': int(team_df['Assists'].max())
            },
            'highest_rated': {
                'name': team_df.loc[team_df['Rating'].idxmax(), 'Player_Name'],
                'rating': float(team_df['Rating'].max())
            }
        }
        
        # Get ML predictions for team performance
        if model is not None and scaler is not None:
            team_features = team_df[feature_columns].mean()
            scaled_features = scaler.transform([team_features])
            predicted_rating = float(model.predict(scaled_features)[0])
            team_stats['predicted_team_rating'] = round(predicted_rating, 1)
            
            # Calculate feature importance for the team
            feature_importance = dict(zip(feature_columns, model.feature_importances_))
            team_stats['feature_importance'] = feature_importance
            
            # Get performance insights
            strengths = []
            weaknesses = []
            for feature in feature_columns:
                team_avg = team_df[feature].mean()
                league_avg = df[feature].mean()
                diff_percent = ((team_avg - league_avg) / league_avg) * 100
                if diff_percent > 10:
                    strengths.append({
                        'feature': feature.replace('_', ' '),
                        'value': round(team_avg, 1),
                        'diff': round(diff_percent, 1)
                    })
                elif diff_percent < -10:
                    weaknesses.append({
                        'feature': feature.replace('_', ' '),
                        'value': round(team_avg, 1),
                        'diff': round(abs(diff_percent), 1)
                    })
            
            team_stats['strengths'] = strengths
            team_stats['weaknesses'] = weaknesses
        
        logger.info(f"Successfully generated team stats for {team}")
        return jsonify(team_stats)
    except Exception as e:
        logger.error(f"Error in get_team_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/<name>')
def get_player(name):
    try:
        logger.info(f"Getting player details for: {name}")
        df = load_data()
        if df is None:
            return jsonify({'error': 'Could not load player data'}), 500
        
        player_df = df[df['Player_Name'] == name]
        if player_df.empty:
            return jsonify({'error': 'Player not found'}), 404
            
        player = player_df.iloc[0].to_dict()
        
        # Get ML prediction for player
        if model is not None and scaler is not None:
            player_features = [player[col] for col in feature_columns]
            scaled_features = scaler.transform([player_features])
            predicted_rating = float(model.predict(scaled_features)[0])
            player['predicted_rating'] = round(predicted_rating, 1)
        
        logger.info(f"Successfully retrieved player details for {name}")
        return jsonify(player)
    except Exception as e:
        logger.error(f"Error in get_player: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feature-importance')
def get_feature_importance():
    try:
        logger.info("Getting feature importance")
        if model is None:
            init_model()  # Initialize model if not already done
            if model is None:  # If still None after initialization
                return jsonify({'error': 'Could not initialize model'}), 500
        
        importance = dict(zip(feature_columns, model.feature_importances_))
        logger.info("Successfully retrieved feature importance")
        return jsonify(importance)
    except Exception as e:
        logger.error(f"Error in get_feature_importance: {str(e)}")
        return jsonify({'error': str(e)}), 500

def normalize_team_name(team_name):
    """Normalize team names to match dataset"""
    team_mapping = {
        # Top 4 teams variations
        'Man City': 'Manchester City',
        'City': 'Manchester City',
        
        'Man United': 'Manchester United',
        'United': 'Manchester United',
        
        'Liverpool FC': 'Liverpool',
        
        'Arsenal FC': 'Arsenal'
    }
    
    # First try exact match
    if team_name in team_mapping:
        return team_mapping[team_name]
    
    # Try case-insensitive match
    lower_name = team_name.lower()
    for key, value in team_mapping.items():
        if key.lower() == lower_name:
            return value
    
    # If no match found, return original name
    return team_name

def get_teams_and_players():
    """Return only top 4 teams"""
    top_teams = [
        'Manchester City', 
        'Arsenal', 
        'Manchester United', 
        'Liverpool'
    ]
    
    teams_data = []
    
    for team in top_teams:
        team_data = {
            'name': team,
            'logo': f'/static/images/{team.lower().replace(" ", "-")}.png'
        }
        teams_data.append(team_data)
    
    return jsonify(teams_data)

@app.route('/get_teams_and_players')
def teams_and_players_route():
    return get_teams_and_players()

@app.route('/get_team_details/<team_name>')
def get_team_details_route(team_name):
    try:
        # Normalize team name
        normalized_team_name = normalize_team_name(team_name)
        logger.info(f"Fetching details for team: {normalized_team_name}")
        
        # Load data
        df = load_data()
        if df is None:
            return jsonify({'error': 'Could not load player data'}), 500
        
        # Validate team is in top 4
        top_teams = [
            'Manchester City', 
            'Arsenal', 
            'Manchester United', 
            'Liverpool'
        ]
        if normalized_team_name not in top_teams:
            return jsonify({'error': f'Team {normalized_team_name} not in top 4'}), 404
        
        # Filter players for the team
        team_players = df[df['Club'] == normalized_team_name]
        
        if team_players.empty:
            return jsonify({'error': f'No players found for team {normalized_team_name}'}), 404
        
        # Prepare player details with safe type conversion
        players_data = []
        for _, player in team_players.iterrows():
            try:
                player_stats = player.to_dict()
                
                # Convert NumPy types to Python native types
                player_details = {
                    'name': str(player_stats['Player_Name']),
                    'position': str(player_stats['Position']),
                    'predicted_rating': float(predict_player_rating(player_stats)),
                    'form': calculate_form(player_stats),
                    'injury_status': get_injury_status(player_stats),
                    'goals': int(player_stats['Goals']),
                    'assists': int(player_stats['Assists']),
                    'pass_accuracy': float(player_stats['Pass_Accuracy']),
                    'shot_accuracy': float(player_stats['Shot_Accuracy'])
                }
                
                players_data.append(player_details)
            except Exception as player_error:
                logger.error(f"Error processing player: {player_error}")
        
        # Calculate team statistics with safe type conversion
        team_stats = {
            'total_goals': int(team_players['Goals'].sum()),
            'total_assists': int(team_players['Assists'].sum()),
            'avg_pass_accuracy': float(team_players['Pass_Accuracy'].mean()),
            'avg_shot_accuracy': float(team_players['Shot_Accuracy'].mean()),
            'total_tackles': int(team_players['Tackles_Won'].sum()),
            'total_passes': int(team_players['Passes_Completed'].sum())
        }
        
        # Team details
        team_details = {
            'team_name': normalized_team_name,
            'team_rating': float(team_players['Rating'].mean()),
            'team_form': calculate_team_form(players_data),
            'formation': get_recommended_formation(players_data),
            'team_stats': team_stats,
            'players': players_data
        }
        
        logger.info(f"Successfully retrieved details for team {normalized_team_name}")
        return jsonify(team_details)
    
    except Exception as e:
        logger.error(f"Error in get_team_details: {str(e)}")
        return jsonify({'error': str(e)}), 500

def calculate_form(player_stats):
    """Calculate player form based on statistics"""
    # Simple form calculation based on goals, assists, and accuracy
    form_score = (
        player_stats['Goals'] * 3 +  # Weight goals heavily
        player_stats['Assists'] * 2 +  # Weight assists moderately
        player_stats['Pass_Accuracy'] / 20 +  # Consider pass accuracy
        player_stats['Shot_Accuracy'] / 20  # Consider shot accuracy
    )
    
    # Convert to 1-5 star rating
    stars = min(5, max(1, round(form_score / 5)))
    return '⭐' * stars

def get_injury_status(player_stats):
    """Simulate injury status based on player statistics"""
    # Use total involvement (goals + assists + tackles) as a proxy for fitness
    total_involvement = player_stats['Goals'] + player_stats['Assists'] + player_stats['Tackles_Won']
    if total_involvement > 10:
        return 'Fit'
    elif total_involvement > 5:
        return 'Light Training'
    else:
        return 'Recovering'

def get_recommended_formation(players):
    """Recommend team formation based on player statistics"""
    # Simple formation recommendation based on team strengths
    attackers = len([p for p in players if p['goals'] > 5])
    midfielders = len([p for p in players if p['assists'] > 5])
    
    if attackers >= 3:
        return '4-3-3'
    elif midfielders >= 4:
        return '4-4-2'
    else:
        return '5-3-2'

def calculate_team_form(players):
    """Calculate overall team form"""
    total_stars = sum(len(p['form']) for p in players)
    avg_stars = total_stars / len(players)
    return '⭐' * round(avg_stars)

def predict_player_rating(player_stats):
    """Predict player rating using the ML model"""
    if model is None or scaler is None:
        return 75  # Default rating if model not initialized
    
    features = np.array([[
        player_stats['Goals'],
        player_stats['Assists'],
        player_stats['Passes_Completed'],
        player_stats['Pass_Accuracy'],
        player_stats['Shot_Accuracy'],
        player_stats['Tackles_Won']
    ]])
    
    scaled_features = scaler.transform(features)
    rating = model.predict(scaled_features)[0]
    return round(float(rating), 1)

if __name__ == '__main__':
    # Initialize model when starting the server
    init_model()
    
    # Get port from environment variable for Docker support
    port = int(os.environ.get('PORT', 5002))
    
    app.run(host='0.0.0.0', port=port, debug=True)
