"""Entrypoint for Anytown Mapper web application."""

from flask import Flask

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'


@app.route('/', methods=['GET'])
def index():
    """Index handler."""
    return 'Anytown Mapper'


if __name__ == '__main__':
    app.run(port=5000)
