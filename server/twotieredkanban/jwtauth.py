import jwt
import jwt.exceptions

TOKEN='auth_token'

def token(secret, **data):
    return jwt.encode(data, secret, algorithm='HS256').decode('utf-8')

def decode(token, secret, key=None):
    try:
        token = jwt.decode(token, secret, algorithms=['HS256'])
        if key:
            return token.get(key)
        else:
            return token
    except jwt.exceptions.DecodeError:
        return None

def save(jar, secret, secure=False, **data):
    jar.set_cookie(TOKEN, token(secret, **data), secure=secure, httponly=True)

def load(jar, secret):
    return decode(jar.cookies.get(TOKEN), secret)