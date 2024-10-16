python3.9 -m venv venv
source venv/bin/activate

# Installing all requirements each registered extension
# needs before starting the Server.
source extensions/install_requirements.sh
install_requirements

pip install wheel
python3 -m pip install -r requirements.txt

export FLASK_APP=app.py
export FLASK_DEBUG=1
export FLASK_RELOAD=1
flask run --with-threads --reload --host=0.0.0.0 --port 3000