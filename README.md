# SHARKdata.se

Source code for the SHARK ("Svenskt HavsARKiv" / "Swedish Ocean Archive") 
data server.

## Development

Installation for development:

    git clone https://github.com/sharkdata/sharkdata_py3.git
    cd sharkdata_py3
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

    # Open a web browser. Address: localhost:8000
