import sys
sys.path.insert(0, "D:\\sign_language_game")
from app import app
app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
