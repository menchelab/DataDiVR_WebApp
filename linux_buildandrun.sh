python3 -m venv venv
source venv/bin/activate
# Installing all requirements each registered extension
# needs before starting the Server.
source extensions/install_requirements.sh
install_requirements

pip install wheel
python -m pip install -r requirements.txt
flask run --host=0.0.0.0 --port 5000

