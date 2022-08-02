from flask import Flask, render_template, request, session, copy_current_request_context
from interactive_functions import search_for_letters
from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError
from checker import check_logged_in
from threading import Thread

app = Flask(__name__)
app.config['dbconfig'] = { 'host': '127.0.0.1',
                           'user': 'vsearch',
                           'password': 'password',
                           'database': 'vsearchlogDB'}
app.secret_key = '1d0edaa72716b43e7c3d605409fdfa9e562d7304be8b08d9f309db3eebf79e60'

@app.route('/login')
def do_login() -> 'str':
    session['logged_in'] = True
    return 'You are now logged in.'

@app.route('/logout')
def do_logout() -> 'str':
    session.pop('logged_in')
    return 'You are now logged out.'

@app.route('/search-for', methods=['POST'])
def do_search() -> 'html':
    
    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """insert into log
                    (phrase, letters, ip, browser_string, results)
                    values
                    (%s, %s, %s, %s, %s)"""
            cursor.execute(_SQL, (req.form['phrase'],
                                req.form['letters'],
                                req.remote_addr,
                                'edge', # must be hardcoded... req.user_agent.browser is not working
                                res,))
    
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Here are your results:'
    results = str(search_for_letters(phrase, letters))
    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except Exception as err:
        print('***** Logging failed with this error:', str(err))
    return render_template('results.html',
                            the_title=title,
                            the_phrase=phrase,
                            the_letters=letters,
                            the_results=results)

@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                            the_title='Welcome to search_for_letters on the web!')

@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = "SELECT phrase, letters, ip, browser_string, results FROM log"
            cursor.execute(_SQL)
            contents = cursor.fetchall()
        titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
        return render_template('viewlog.html',
                                the_title='View Log',
                                the_row_titles=titles,
                                the_data=contents)
    except ConnectionError as err:
        print('There was a problem connecting to the database. Error:', str(err))
    except CredentialsError as err:
        print('User id/Password issues. Error:', str(err))
    except SQLError as err:
        print('Something went wrong with your query. Error:', str(err))
    except Exception as err:
        print('Something went wrong. Error:', str(err))

if __name__ == '__main__':
    app.run(debug=True)