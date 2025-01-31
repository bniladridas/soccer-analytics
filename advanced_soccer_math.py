import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

class SoccerMathAnalytics:
    def __init__(self, df=None, data_path='/Users/niladridas/Documents/ml-soccer/data/player_stats.csv'):
        """
        Initialize Soccer Math Analytics
        
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
        
        # Ensure data is processed
        self._process_data()
        
    def _process_data(self):
        """Process and prepare data for analytics"""
        # Add any necessary preprocessing steps
        # Convert columns to appropriate types if needed
        numeric_columns = ['Goals', 'Assists', 'Passes_Completed', 
                           'Pass_Accuracy', 'Shot_Accuracy', 'Tackles_Won']
        
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Drop rows with missing data if necessary
        self.df.dropna(subset=numeric_columns, inplace=True)
        
        # Create performance score column
        self._calculate_performance_score()
    
    def _calculate_performance_score(self):
        """Calculate a comprehensive performance score for players"""
        # Weighted calculation of performance
        weights = {
            'Goals': 0.3,
            'Assists': 0.2,
            'Pass_Accuracy': 0.15,
            'Shot_Accuracy': 0.2,
            'Tackles_Won': 0.15
        }
        
        # Normalize each metric
        normalized_df = self.df.copy()
        for metric in weights.keys():
            normalized_df[metric] = (self.df[metric] - self.df[metric].min()) / (self.df[metric].max() - self.df[metric].min())
        
        # Calculate weighted performance score
        self.df['Performance_Score'] = sum(
            normalized_df[metric] * weight 
            for metric, weight in weights.items()
        ) * 100
        
        # Round to 2 decimal places
        self.df['Performance_Score'] = self.df['Performance_Score'].round(2)
        
    def team_performance_analysis(self):
        """
        Comprehensive team performance mathematical analysis
        
        Returns:
        - Team-level statistical summary
        - Performance distribution
        - Comparative metrics
        """
        team_performance = self.df.groupby('Club').agg({
            'Performance_Score': ['mean', 'std', 'median'],
            'Goals': ['sum', 'mean'],
            'Assists': ['sum', 'mean'],
            'Pass_Accuracy': 'mean',
            'Shot_Accuracy': 'mean'
        })
        
        # Z-score for team performance comparison
        team_performance['Performance_Z_Score'] = stats.zscore(team_performance[('Performance_Score', 'mean')])
        
        return team_performance
    
    def player_performance_distribution(self):
        """
        Detailed statistical distribution of player performances
        
        Mathematical Techniques:
        - Kernel Density Estimation
        - Descriptive Statistics
        - Probability Distributions
        """
        # Kernel Density Estimation
        plt.figure(figsize=(12, 6))
        for team in self.df['Club'].unique():
            team_data = self.df[self.df['Club'] == team]['Performance_Score']
            team_data.plot.kde(label=team)
        
        plt.title('Player Performance Distribution by Team')
        plt.xlabel('Performance Score')
        plt.ylabel('Density')
        plt.legend()
        plt.tight_layout()
        plt.savefig('/Users/niladridas/Documents/ml-soccer/data/performance_distribution.png')
        plt.close()
        
        # Statistical Summary
        return {
            'overall_stats': self.df['Performance_Score'].describe(),
            'team_performance_summary': self.team_performance_analysis()
        }
    
    def correlation_matrix(self):
        """
        Advanced correlation analysis of player metrics
        
        Mathematical Techniques:
        - Pearson Correlation
        - Spearman Rank Correlation
        """
        numeric_columns = ['Goals', 'Assists', 'Pass_Accuracy', 'Shot_Accuracy', 'Performance_Score']
        correlation_pearson = self.df[numeric_columns].corr(method='pearson')
        correlation_spearman = self.df[numeric_columns].corr(method='spearman')
        
        plt.figure(figsize=(10, 8))
        plt.subplot(1, 2, 1)
        plt.title('Pearson Correlation')
        plt.imshow(correlation_pearson, cmap='coolwarm', aspect='auto')
        plt.colorbar()
        plt.xticks(range(len(numeric_columns)), numeric_columns, rotation=45)
        plt.yticks(range(len(numeric_columns)), numeric_columns)
        
        plt.subplot(1, 2, 2)
        plt.title('Spearman Correlation')
        plt.imshow(correlation_spearman, cmap='coolwarm', aspect='auto')
        plt.colorbar()
        plt.xticks(range(len(numeric_columns)), numeric_columns, rotation=45)
        plt.yticks(range(len(numeric_columns)), numeric_columns)
        
        plt.tight_layout()
        plt.savefig('/Users/niladridas/Documents/ml-soccer/data/correlation_matrix.png')
        plt.close()
        
        return {
            'pearson_correlation': correlation_pearson,
            'spearman_correlation': correlation_spearman
        }
    
    def predictive_player_rating(self):
        """
        Machine Learning inspired predictive player rating
        
        Mathematical Techniques:
        - Linear Regression
        - Feature Importance
        - Predictive Scoring
        """
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        
        # Prepare features
        features = ['Goals', 'Assists', 'Pass_Accuracy', 'Shot_Accuracy']
        X = self.df[features]
        y = self.df['Performance_Score']
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Linear Regression
        model = LinearRegression()
        model.fit(X_scaled, y)
        
        # Feature importance
        feature_importance = pd.Series(
            np.abs(model.coef_), 
            index=features
        ).sort_values(ascending=False)
        
        return {
            'feature_importance': feature_importance,
            'model_score': model.score(X_scaled, y)
        }

# Run analysis
if __name__ == '__main__':
    soccer_math = SoccerMathAnalytics()
    
    print("🔢 Team Performance Analysis:")
    print(soccer_math.team_performance_analysis())
    
    print("\n📊 Player Performance Distribution:")
    performance_dist = soccer_math.player_performance_distribution()
    print(performance_dist['overall_stats'])
    
    print("\n🧮 Correlation Matrix:")
    correlations = soccer_math.correlation_matrix()
    print("Pearson Correlation:\n", correlations['pearson_correlation'])
    
    print("\n🤖 Predictive Player Rating:")
    predictive_rating = soccer_math.predictive_player_rating()
    print("Feature Importance:\n", predictive_rating['feature_importance'])
    print("Model Predictive Score:", predictive_rating['model_score'])
