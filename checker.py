from flask import session
from functools import wraps

def check_logged_in(func: 'function') -> 'function':
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        return 'You need to be logged in to view this page.'
    return wrapper