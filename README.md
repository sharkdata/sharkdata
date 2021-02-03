# SHARKdata.se

Source code for the SHARK ("Svenskt HavsARKiv" / "Swedish Ocean Archive") 
data server.

## Development

Installation for development:

    git clone https://github.com/sharkdata/sharkdata.git
    cd sharkdata
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    # For production, not needed in debug mode:
    python manage.py collectstatic

Open a web browser. Address: localhost:8000

## Add data

    - Add datasets (as zip files) and resources to "./data_in".
    - TBD.

## Production

Docker can be used production.
More info: https://github.com/sharkdata/docker

## Contact

TBD
