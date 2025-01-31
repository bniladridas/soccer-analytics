import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns

class PlayerRecommendationSystem:
    def __init__(self, df=None, data_path='/Users/niladridas/Documents/ml-soccer/data/player_stats.csv'):
        """
        Initialize Player Recommendation System
        
        Args:
            df (pd.DataFrame, optional): Existing DataFrame. Defaults to None.
            data_path (str, optional): Path to player stats CSV. Defaults to standard location.
        """
        if df is not None:
            self.df = df
        else:
            try:
                self.df = pd.read_csv(data_path)
            except Exception as e:
                print(f"Error reading data: {e}")
                self.df = pd.DataFrame()  # Fallback to empty DataFrame
        
        # Preprocess data
        self._preprocess_data()
        
    def _preprocess_data(self):
        """Preprocess data for recommendation system"""
        # Ensure numeric columns
        numeric_columns = [
            'Goals', 'Assists', 'Passes_Completed', 
            'Pass_Accuracy', 'Shot_Accuracy', 'Tackles_Won'
        ]
        
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Drop rows with missing data
        self.df.dropna(subset=numeric_columns, inplace=True)
        
        # One-hot encode categorical variables
        self.df = pd.get_dummies(self.df, columns=['Position', 'Club'])
        
        # Normalize features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        feature_columns = [
            'Goals', 'Assists', 'Passes_Completed', 
            'Pass_Accuracy', 'Shot_Accuracy', 'Tackles_Won'
        ]
        self.df[feature_columns] = scaler.fit_transform(self.df[feature_columns])
        
        # Create advanced features
        self.df['Goal_Contribution'] = self.df['Goals'] + 0.5 * self.df['Assists']
        self.df['Efficiency_Score'] = (
            self.df['Pass_Accuracy'] * 0.4 + 
            self.df['Shot_Accuracy'] * 0.4 + 
            self.df['Goal_Contribution'] * 0.2
        )
        
        # Prepare features for similarity and prediction
        self.feature_columns = [
            'Goals', 'Assists', 'Pass_Accuracy', 
            'Shot_Accuracy', 'Tackles_Won', 
            'Position_Forward', 'Position_Midfielder', 
            'Position_Defender', 'Position_Goalkeeper'
        ]
        
        # Combine features
        self.features = self.df[self.feature_columns]
        
        # Standardize features
        self.scaler = StandardScaler()
        self.features_scaled = self.scaler.fit_transform(self.features)
    
    def find_similar_players(self, player_name, top_n=5):
        """
        Find players most similar to a given player
        
        Similarity Metrics:
        - Cosine Similarity
        - Multi-dimensional Feature Comparison
        """
        # Find player index
        player_index = self.df[self.df['Player_Name'] == player_name].index
        
        if len(player_index) == 0:
            raise ValueError(f"Player {player_name} not found in dataset")
        
        player_index = player_index[0]
        
        # Compute cosine similarity
        similarities = cosine_similarity(
            self.features_scaled[player_index].reshape(1, -1), 
            self.features_scaled
        )[0]
        
        # Sort and get top similar players
        similar_indices = similarities.argsort()[::-1][1:top_n+1]
        
        similar_players = self.df.iloc[similar_indices].copy()
        similar_players['Similarity_Score'] = similarities[similar_indices]
        
        return similar_players[['Player_Name', 'Club', 'Position', 'Similarity_Score']]
    
    def predict_player_performance(self, features=None):
        """
        Machine Learning Performance Prediction
        
        Techniques:
        - Random Forest Regression
        - Feature Importance Analysis
        - Performance Forecasting
        """
        # Prepare training data
        X = self.features_scaled
        y = self.df['Efficiency_Score']
        
        # Train Random Forest Regressor
        rf_model = RandomForestRegressor(
            n_estimators=100, 
            random_state=42
        )
        rf_model.fit(X, y)
        
        # Feature importance visualization
        plt.figure(figsize=(10, 6))
        feature_importance = pd.Series(
            rf_model.feature_importances_, 
            index=self.feature_columns
        ).sort_values(ascending=False)
        
        sns.barplot(x=feature_importance.values, y=feature_importance.index)
        plt.title('Feature Importance in Player Performance')
        plt.xlabel('Importance Score')
        plt.tight_layout()
        plt.savefig('/Users/niladridas/Documents/ml-soccer/data/feature_importance.png')
        plt.close()
        
        # If specific features provided, predict performance
        if features is not None:
            features_scaled = self.scaler.transform(features)
            predicted_performance = rf_model.predict(features_scaled)
            return predicted_performance
        
        return {
            'model': rf_model,
            'feature_importance': feature_importance
        }
    
    def position_based_recommendations(self, position, top_n=3):
        """
        Position-specific player recommendations
        
        Recommendation Strategy:
        - Filter by position
        - Rank by performance metrics
        """
        position_players = self.df[self.df['Position'] == position]
        
        # Rank players by efficiency score
        ranked_players = position_players.sort_values(
            by='Efficiency_Score', 
            ascending=False
        ).head(top_n)
        
        return ranked_players[['Player_Name', 'Club', 'Efficiency_Score']]
    
    def generate_player_insights(self):
        """
        Comprehensive player performance insights
        
        Generates:
        - Performance distribution
        - Position-wise analytics
        - Team comparisons
        """
        insights = {
            'overall_performance': {
                'mean': self.df['Efficiency_Score'].mean(),
                'median': self.df['Efficiency_Score'].median(),
                'std': self.df['Efficiency_Score'].std()
            },
            'position_performance': self.df.groupby('Position')['Efficiency_Score'].agg(['mean', 'median', 'std']),
            'team_performance': self.df.groupby('Club')['Efficiency_Score'].agg(['mean', 'median', 'std'])
        }
        
        # Visualize performance distribution
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='Position', y='Efficiency_Score', data=self.df)
        plt.title('Player Efficiency Score by Position')
        plt.tight_layout()
        plt.savefig('/Users/niladridas/Documents/ml-soccer/data/position_performance.png')
        plt.close()
        
        return insights

# Example usage and testing
if __name__ == '__main__':
    # Initialize recommendation system
    rec_system = PlayerRecommendationSystem()
    
    # Demonstrate key functionalities
    print("🔍 Similar Players to Mohamed Salah:")
    print(rec_system.find_similar_players('Mohamed Salah'))
    
    print("\n🏆 Top Forward Recommendations:")
    print(rec_system.position_based_recommendations('Forward'))
    
    print("\n📊 Player Performance Insights:")
    insights = rec_system.generate_player_insights()
    print(insights)
    
    # Predict performance and show feature importance
    performance_model = rec_system.predict_player_performance()
    print("\n🧠 Feature Importance:")
    print(performance_model['feature_importance'])
