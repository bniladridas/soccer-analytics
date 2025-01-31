import os
import requests
from PIL import Image
from io import BytesIO

# Create images directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

# Dictionary of team logos with their URLs (using Wikipedia and official sources)
team_logos = {
    'premier-league': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f2/Premier_League_Logo.svg/1200px-Premier_League_Logo.svg.png',
    'arsenal': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Arsenal_FC.svg/1200px-Arsenal_FC.svg.png',
    'aston-villa': 'https://i.imgur.com/jSPWIEn.png',
    'bournemouth': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/AFC_Bournemouth_%282013%29.svg/1200px-AFC_Bournemouth_%282013%29.svg.png',
    'brentford': 'https://upload.wikimedia.org/wikipedia/en/thumb/2/2a/Brentford_FC_crest.svg/1200px-Brentford_FC_crest.svg.png',
    'brighton': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/fd/Brighton_%26_Hove_Albion_logo.svg/1200px-Brighton_%26_Hove_Albion_logo.svg.png',
    'burnley': 'https://i.imgur.com/9VGFxTM.png',
    'chelsea': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/cc/Chelsea_FC.svg/1200px-Chelsea_FC.svg.png',
    'crystal-palace': 'https://i.imgur.com/2MHtxGQ.png',
    'everton': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/7c/Everton_FC_logo.svg/1200px-Everton_FC_logo.svg.png',
    'fulham': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Fulham_FC_%28shield%29.svg/1200px-Fulham_FC_%28shield%29.svg.png',
    'liverpool': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Liverpool_FC.svg/1200px-Liverpool_FC.svg.png',
    'luton': 'https://i.imgur.com/KZnhh8j.png',
    'manchester-city': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Manchester_City_FC_badge.svg/1200px-Manchester_City_FC_badge.svg.png',
    'manchester-united': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/7a/Manchester_United_FC_crest.svg/1200px-Manchester_United_FC_crest.svg.png',
    'newcastle': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Newcastle_United_Logo.svg/1200px-Newcastle_United_Logo.svg.png',
    'nottingham-forest': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/Nottingham_Forest_F.C._logo.svg/1200px-Nottingham_Forest_F.C._logo.svg.png',
    'sheffield-united': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9c/Sheffield_United_FC_logo.svg/1200px-Sheffield_United_FC_logo.svg.png',
    'tottenham': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b4/Tottenham_Hotspur.svg/1200px-Tottenham_Hotspur.svg.png',
    'west-ham': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/West_Ham_United_FC_logo.svg/1200px-West_Ham_United_FC_logo.svg.png',
    'wolves': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/fc/Wolverhampton_Wanderers.svg/1200px-Wolverhampton_Wanderers.svg.png'
}

def download_and_process_logo(name, url):
    try:
        # Download image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Open and process image
        img = Image.open(BytesIO(response.content))
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Resize to 48x48 while maintaining aspect ratio
        aspect_ratio = img.width / img.height
        if aspect_ratio > 1:
            new_width = 48
            new_height = int(48 / aspect_ratio)
        else:
            new_height = 48
            new_width = int(48 * aspect_ratio)
            
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with padding to make it 48x48
        new_img = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
        x_offset = (48 - new_width) // 2
        y_offset = (48 - new_height) // 2
        new_img.paste(img, (x_offset, y_offset), img)
        
        # Save processed image
        output_path = f'static/images/{name}.png'
        new_img.save(output_path, 'PNG')
        print(f'Successfully processed {name}')
        
    except Exception as e:
        print(f'Error processing {name}: {str(e)}')

# Download and process all logos
for team_name, logo_url in team_logos.items():
    print(f'Processing {team_name}...')
    download_and_process_logo(team_name, logo_url)

print('All logos have been processed!')
