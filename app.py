from flask import Flask

def create_app(**config_overrides):
	app = Flask(__name__)

	# Load config
	app.config.from_pyfile('settings.py')

	# Apply overrides for tests
	app.config.update(config_overrides)

	# Import blueprints
	from home.views import home_app
	
	# Register blueprints
	app.register_blueprint(home_app)

	return app