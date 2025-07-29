from app import create_app
import logging

if __name__ == '__main__':
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    app = create_app('development')
    app.run(debug=True, host="0.0.0.0", port=5000)
