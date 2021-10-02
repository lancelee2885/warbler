# Warbler

Warbler is a Twitter clone that uses technologies including Flask, PostgreSQL, and SQLAlchemy, on the back-end and Jinja templating, jQuery, and Axios on the front-end. 

For this project I have: 
* fixed bugs in current user profile model by understanding existing codebase. 
* added profile editing functionality
* added feature for a user to like a warble posted by other users and further built this functionality using AJAX request on the front end
* wrote extensive tests ensure functionalities without manually testing on in developing environment.

You can view a deployed version [here](https://warbler-ivan-lance.herokuapp.com/).

<br>

## Documentation

A fully written documentation can be found [here](https://lancelee2885.github.io/warbler/docs/_build/html)

<br>

## Installation and Setup Instructions

1. Clone this repository
2. Create a virtual environment
    * `python3 -m venv venv`
    * `source venv/bin/activate`
    * `pip3 install -r requirements.txt`
3. Create the database
    * `createdb warbler`
    * `python3 seed.py`
4. Start the server
    * `flask run`

<br>

## Testing:
1. Create the database
    * `createdb warbler-test`
2. Run tests:
    * To run all: `python3 -m unittest`
    * To run specific file: `python3 -m unittest test_file_to_run.py`

<br>

## Technologies Used

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - Web Development
  Framework
* [Flask-WTForms](https://flask-wtf.readthedocs.io/en/stable/) - integration of
  Flask and WTForms library, including CSRF protection
* [PostgreSQL Database](https://www.postgresql.org/) - SQL database management
  system
* [SQLAlchemy](https://www.sqlalchemy.org/) - database ORM
* [Jinja](https://palletsprojects.com/p/jinja/) - templating engine 

<br>

## Authors

This project is authored by [Lance Lee](https://github.com/lancelee2885) and Ivan Yang(https://github.com/magus0)