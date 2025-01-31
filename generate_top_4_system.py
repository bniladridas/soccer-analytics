import pandas as pd
import numpy as np
import random
import os

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

# Positions with their typical distribution for top teams
positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
position_weights = [0.15, 0.30, 0.30, 0.25]

# Function to generate realistic player stats
def generate_player_stats(position, player_name=None):
    # Adjust base rating and stats for known players
    if player_name in [
        'Erling Haaland', 'Kevin De Bruyne', 'Mohamed Salah', 'Virgil van Dijk', 
        'Bruno Fernandes', 'Bukayo Saka', 'Martin Odegaard'
    ]:
        base_rating = random.uniform(85, 92)
    else:
        base_rating = random.uniform(70, 85)
    
    if position == 'Goalkeeper':
        return {
            'Rating': base_rating,
            'Goals': random.randint(0, 1),
            'Assists': random.randint(0, 2),
            'Passes_Completed': random.randint(50, 300),
            'Pass_Accuracy': random.uniform(75, 95),
            'Shot_Accuracy': random.uniform(40, 60),
            'Tackles_Won': random.randint(20, 100)
        }
    elif position == 'Defender':
        return {
            'Rating': base_rating,
            'Goals': random.randint(0, 5),
            'Assists': random.randint(0, 5),
            'Passes_Completed': random.randint(100, 500),
            'Pass_Accuracy': random.uniform(80, 95),
            'Shot_Accuracy': random.uniform(50, 75),
            'Tackles_Won': random.randint(50, 200)
        }
    elif position == 'Midfielder':
        return {
            'Rating': base_rating,
            'Goals': random.randint(3, 15),
            'Assists': random.randint(5, 20),
            'Passes_Completed': random.randint(200, 700),
            'Pass_Accuracy': random.uniform(85, 95),
            'Shot_Accuracy': random.uniform(60, 85),
            'Tackles_Won': random.randint(30, 150)
        }
    else:  # Forward
        return {
            'Rating': base_rating,
            'Goals': random.randint(10, 30),
            'Assists': random.randint(5, 15),
            'Passes_Completed': random.randint(50, 300),
            'Pass_Accuracy': random.uniform(70, 85),
            'Shot_Accuracy': random.uniform(75, 90),
            'Tackles_Won': random.randint(10, 50)
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
            'Position': position
        }
        
        # Add stats
        player.update(generate_player_stats(position, player_name))
        
        all_players.append(player)

# Create DataFrame
df = pd.DataFrame(all_players)

# Save to CSV
os.makedirs('/Users/niladridas/Documents/ml-soccer/data', exist_ok=True)
df.to_csv('/Users/niladridas/Documents/ml-soccer/data/player_stats.csv', index=False)

print(f"Generated dataset with {len(df)} players across {len(top_teams)} top teams")
print("\nDataset Preview:")
print(df)
print("\nTeam Distribution:")
print(df['Club'].value_counts())
print("\nPosition Distribution:")
print(df['Position'].value_counts())
