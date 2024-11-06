import os
from dotenv import load_dotenv
from config import create_app, config_dict
import cloudinary

# Load environment variables from .env file
load_dotenv()

config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config_dict[config_name])

if __name__ == '__main__':
    app.run()