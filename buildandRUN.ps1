$host.ui.RawUI.WindowTitle = 'DataSerVR'
$host.UI.RawUI.BackgroundColor='darkgray'

Clear-Host
#create virtual env in windows and activate it and install requirements.txt
py -3.9 -m venv venv
venv\Scripts\activate

# Install requirements of the extensions
. .\extensions\install_requirements.ps1
Install-Requirements

#pip install flask_cors
#pip install pymysql
pip install wheel
python -m pip install -r requirements.txt
$env:FLASK_ENV="development"
$env:FLASK_APP="app.py"
#flask run --port 5000
flask run --with-threads --host=0.0.0.0 --port 5000
#python app.py
