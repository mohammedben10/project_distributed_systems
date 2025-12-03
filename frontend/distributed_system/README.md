#create ur virtual env
python -m venv venv
venv\Scripts\activate

#install packages
pip install -r requirements.txt

#run project
python manage.py runserver
