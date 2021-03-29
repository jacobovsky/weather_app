from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import sys


app = Flask(__name__)
app.config['SECRET_KEY'] = 'wierogjlskanfaij2394293fj2if0w3290jfpasjf902jr2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)


# noinspection PyUnresolvedReferences
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


db.create_all()


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        api_key = 'd36b46a551d347ed2a0c2b87137c83da'
        req = requests.request('GET', 'http://api.openweathermap.org/data/2.5/weather?q={}&appid='
                                      'd36b46a551d347ed2a0c2b87137c83da'.format(request.form['city_name']))
        context = req.json()

        # get names of previously typed cities from db
        cities = City.query.all()
        cities_names = [city.name for city in cities]

        # check if user input is valid name of existing city
        # or if typed city name has been already searched before.
        if str(context['cod'])[0] == '4':
            flash("The city doesn't exist!")
            return redirect('/')
        elif context['name'] in cities_names:
            flash("The city has already been added to the list!")
            return redirect('/')

        # database
        db_data = City(name=context['name'])
        db.session.add(db_data)
        db.session.commit()
        # return render_template('index_3.html', context=context)
        return redirect('/')
    else:
        # get names of previously typed cities from db
        cities = City.query.all()
        cities_names = [city.name for city in cities]

        # based on previously searched cities gather info about them
        reqs = []
        for city_name in cities_names:
            reqs.append(requests.request('GET', 'http://api.openweathermap.org/data/2.5/weather?q={}&appid='
                                         'd36b46a551d347ed2a0c2b87137c83da'.format(city_name)).json())
        return render_template('index.html', context=reqs)


@app.route('/delete/<city_name>', methods=['GET', 'POST'])
def delete(city_name):
    if request.method == 'POST':
        city = City.query.filter_by(name=city_name).first()
        db.session.delete(city)
        db.session.commit()
        return redirect('/')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
