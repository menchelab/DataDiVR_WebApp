python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_DEBUG=1
export FLASK_RELOAD=1
flask run --with-threads --reload --host=0.0.0.0 --port 3000

