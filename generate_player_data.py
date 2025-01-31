import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
np.random.seed(42)

# List of Premier League teams for the 2023-2024 season
teams = [
    'Manchester City', 'Arsenal', 'Liverpool', 'Aston Villa', 
    'Tottenham', 'Manchester United', 'Newcastle United', 
    'West Ham United', 'Chelsea', 'Brighton', 'Brentford', 
    'Crystal Palace', 'Wolverhampton', 'Bournemouth', 
    'Fulham', 'Everton', 'Nottingham Forest', 'Luton', 
    'Sheffield United', 'Burnley'
]

# Positions with their typical distribution
positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
position_weights = [0.15, 0.30, 0.30, 0.25]

# Function to generate player name
def generate_player_name():
    first_names = [
        'James', 'Michael', 'John', 'David', 'Daniel', 'Thomas', 
        'Jack', 'Harry', 'William', 'Oliver', 'Charlie', 'George', 
        'Liam', 'Ethan', 'Noah', 'Mohamed', 'Kevin', 'Bruno', 
        'Marcus', 'Virgil', 'Rodri', 'Erling', 'Gabriel', 'Martin'
    ]
    last_names = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 
        'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Kane', 'Salah', 
        'De Bruyne', 'Fernandes', 'van Dijk', 'Haaland', 'Silva', 
        'Jesus', 'Saka', 'Rice', 'Odegaard', 'Dias'
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Function to generate realistic player stats
def generate_player_stats(position):
    base_rating = random.uniform(60, 90)
    
    if position == 'Goalkeeper':
        return {
            'Rating': base_rating,
            'Goals': random.randint(0, 2),
            'Assists': random.randint(0, 3),
            'Passes_Completed': random.randint(50, 300),
            'Pass_Accuracy': random.uniform(70, 95),
            'Shot_Accuracy': random.uniform(40, 70),
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
            'Goals': random.randint(2, 15),
            'Assists': random.randint(3, 20),
            'Passes_Completed': random.randint(200, 700),
            'Pass_Accuracy': random.uniform(85, 95),
            'Shot_Accuracy': random.uniform(60, 85),
            'Tackles_Won': random.randint(30, 150)
        }
    else:  # Forward
        return {
            'Rating': base_rating,
            'Goals': random.randint(5, 30),
            'Assists': random.randint(3, 15),
            'Passes_Completed': random.randint(50, 300),
            'Pass_Accuracy': random.uniform(70, 85),
            'Shot_Accuracy': random.uniform(70, 90),
            'Tackles_Won': random.randint(10, 50)
        }

# Generate player data
all_players = []
for team in teams:
    # Number of players per team (15-25 range)
    num_players = random.randint(15, 25)
    
    for _ in range(num_players):
        # Choose position based on weighted distribution
        position = np.random.choice(positions, p=position_weights)
        
        # Generate player
        player = {
            'Player_Name': generate_player_name(),
            'Club': team,
            'Position': position
        }
        
        # Add stats
        player.update(generate_player_stats(position))
        
        all_players.append(player)

# Create DataFrame
df = pd.DataFrame(all_players)

# Shuffle the DataFrame to mix players
df = df.sample(frac=1).reset_index(drop=True)

# Save to CSV
df.to_csv('/Users/niladridas/Documents/ml-soccer/data/player_stats.csv', index=False)

print(f"Generated dataset with {len(df)} players across {len(teams)} teams")
print("\nDataset Preview:")
print(df.head())
print("\nTeam Distribution:")
print(df['Club'].value_counts())
print("\nPosition Distribution:")
print(df['Position'].value_counts())
