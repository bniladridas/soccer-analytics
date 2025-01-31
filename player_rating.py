import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

class PlayerRatingSystem:
    def __init__(self):
        self.data = None
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_columns = [
            'Goals', 'Assists', 'Passes_Completed', 'Tackles_Won',
            'Interceptions', 'Clean_Sheets', 'Shot_Accuracy', 'Pass_Accuracy',
            'Minutes_Played'
        ]

    def load_data(self, file_path):
        """Load player statistics from CSV file"""
        self.data = pd.read_csv(file_path)
        print(f"Loaded {len(self.data)} players from {file_path}")

    def prepare_features(self):
        """Prepare features for model training"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data first.")
        
        print("Preparing features...")
        # Scale the features
        X = self.data[self.feature_columns]
        self.X_scaled = self.scaler.fit_transform(X)
        
        # Calculate initial ratings based on weighted sum of normalized features
        weights = {
            'Goals': 0.25,
            'Assists': 0.15,
            'Passes_Completed': 0.1,
            'Tackles_Won': 0.1,
            'Interceptions': 0.1,
            'Clean_Sheets': 0.05,
            'Shot_Accuracy': 0.1,
            'Pass_Accuracy': 0.1,
            'Minutes_Played': 0.05
        }
        
        # Initialize ratings between 75-95 based on weighted features
        normalized_features = (X - X.min()) / (X.max() - X.min())
        self.data['Initial_Rating'] = sum(normalized_features[col] * weight 
                                        for col, weight in weights.items()) * 20 + 75
        print("Features prepared successfully")

    def train_model(self):
        """Train the Random Forest model"""
        if not hasattr(self, 'X_scaled'):
            raise ValueError("Features not prepared. Call prepare_features first.")
        
        print("Training model...")
        self.model.fit(self.X_scaled, self.data['Initial_Rating'])
        print("Model trained successfully")

    def predict_ratings(self):
        """Predict player ratings using the trained model"""
        if not hasattr(self, 'X_scaled'):
            raise ValueError("Model not trained. Call train_model first.")
        
        print("Predicting ratings...")
        predictions = self.model.predict(self.X_scaled)
        self.data['Predicted_Rating'] = predictions.round(1)
        
        # Ensure ratings are within reasonable bounds (70-99)
        self.data['Predicted_Rating'] = self.data['Predicted_Rating'].clip(70, 99)
        print(f"Predicted ratings for {len(self.data)} players")
        
        # Print some sample predictions
        print("\nSample predictions:")
        print(self.data[['Player_Name', 'Club', 'Predicted_Rating']].head())

    def get_feature_importance(self):
        """Get feature importance from the trained model"""
        if not hasattr(self, 'model') or not hasattr(self, 'feature_columns'):
            raise ValueError("Model not trained. Call train_model first.")
        
        importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        })
        importance = importance.sort_values('importance', ascending=False)
        
        print("\nFeature Importance:")
        print(importance.to_string(index=False))
        return importance

    def analyze_mu_players(self):
        """Analyze Manchester United players specifically"""
        self.predict_ratings()  # Make sure we have predictions first
        mu_ratings = self.data[self.data['Club'] == 'Manchester United'].copy()
        mu_ratings = mu_ratings.sort_values('Predicted_Rating', ascending=False)
        
        print("\nManchester United Player Ratings:")
        print(mu_ratings[['Player_Name', 'Predicted_Rating']].to_string())
        
        # Create visualization
        plt.figure(figsize=(12, 6))
        sns.barplot(data=mu_ratings.head(10), 
                   x='Player_Name', 
                   y='Predicted_Rating')
        plt.xticks(rotation=45)
        plt.title('Top 10 Manchester United Players by Rating')
        plt.tight_layout()
        plt.savefig('mu_player_ratings.png')

def main():
    # Initialize the rating system
    rating_system = PlayerRatingSystem()
    
    try:
        # Load data
        rating_system.load_data('player_stats.csv')
        
        # Prepare and train model
        rating_system.prepare_features()
        rating_system.train_model()
        
        # Generate predictions and analysis
        rating_system.predict_ratings()
        rating_system.analyze_mu_players()
        rating_system.get_feature_importance()
        
    except FileNotFoundError:
        print("Error: player_stats.csv file not found. Please ensure the data file exists.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
