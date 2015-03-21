import sys
from shittyLetters import app, setup_db

if __name__ == "__main__":
  if len(sys.argv) > 1:
    setup_db(seed=True)
  else:
    app.run(debug=True)
