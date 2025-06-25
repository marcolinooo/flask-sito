from waitress import serve
from app import app  # importa la tua app Flask dal file app.py

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8000)
