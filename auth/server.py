import jwt
import datetime
import os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))  # type:int


# endpoints
@server.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth:
        return 'missing credientials', 401

    # check db for username and password
    cur = mysql.connection.cursor()
    query = 'SELECT email, password FROM user WHERE email= "{}"'.format(
        auth.username)
    res = cur.execute(query)

    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if (auth.username != email or auth.password != password):
            return 'invalid credientials', 401
        else:
            return create_JWT(auth.username, str(os.environ.get('JWT_SECRET')), True)

    else:  # user not found
        return 'invalid credentials', 401


def create_JWT(username, secret, authz):
    return jwt.encode(
        {
            'username': username,
            'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'admin': authz,
        },
        secret,
        algorithm='HS256',  # algorithm: str | None = 'HS256'
    )


@server.route('/validate', methods=['POST'])
def validate():
    encoded_jwt = request.headers['Authorization']

    if not encoded_jwt:
        return 'missing credentials', 401

    encoded_jwt = encoded_jwt.split(' ')[1]

    try:
        decoded = jwt.decode(
            encoded_jwt,
            os.environ.get('JWT_SECRET'),
            algorithms=['HS256'],  # algorithms: List[str]
        )
    except:
        return 'not authorized', 403

    return decoded, 200


if __name__ == "__main__":
    server.run(host='0.0.0.0', port=5500)
