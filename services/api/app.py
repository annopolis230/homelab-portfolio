from flask import Flask, jsonify, request, abort
from cryptography.fernet import Fernet
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import hmac
import mysql.connector
import requests

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2)

class UnauthorizedException(Exception):
        pass

class DatabaseConnectionException(Exception):
        pass

def get_secret(secret):
        with open(f'{os.getenv(secret)}') as f:
                return f.read().strip()

limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        meta_limits=["2/hour", "4/day"],
        default_limits=["10/minute"],
        storage_uri=f'redis://:{get_secret("REDIS_PASSWORD")}@redis:6379/2',
        key_prefix='lightworks_api'
)

def verify_request(secret, headers):
        received_secret = headers.get('x-api-key')
        if not received_secret:
                app.logger.warning(f'No API key provided from {headers.get("x-forwarded-for")}') 
                raise UnauthorizedException("No API key")
        else:
                received_secret = received_secret.encode()
        if not hmac.compare_digest(received_secret, secret):
                app.logger.warning(f'Invalid API key from {headers.get("x-forwarded-for")}')
                raise UnauthorizedException("Invalid API key")

def http_get(headers, uri, timeout=10):
        try:
                response = requests.get(str(uri), timeout=timeout, headers=headers)
                code = response.status_code
                response.raise_for_status()
                data = response.json()
                return data
        except requests.exceptions.HTTPError as err:
                app.logger.warning(f'HTTP error occured sending to {uri}: {err}')
                return jsonify({'An error was returned from the API endpoint': str(err)}), code
        except requests.exceptions.Timeout as err:
                app.logger.warning(f'Timeout occured sending to {uri}: {err}')
                return jsonify({'An error was returned from the API endpoint': str(err)}), code
        except request.exceptions.RequestException as err:
                app.logger.warning(f'An error occured sending to {uri}: {err}')
                return jsonify({'An error was returned from the API endpoint': str(err)}), code
        return None

def fetch_key(name):
        key = get_secret("ENCRYPTION_KEY").encode()
        cipher_suite = Fernet(key)

        try:
                connection = mysql.connector.connect(
                        host=os.getenv("MARIADB_HOST"),
                        user=os.getenv("MARIADB_USER"),
                        password=get_secret("MARIADB_PASSWORD"),
                        database=os.getenv("MARIADB_DATABASE")
                )
        except:
                raise DatabaseConnectionException("Unable to connect to internal db")

        cursor = connection.cursor()
        query = "SELECT api_key FROM api_keys WHERE name = %s"
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        connection.close()
        if result:
                return cipher_suite.decrypt(result[0])
        else:
                raise DatabaseConnectionException("No API key found")

@app.route('/group', methods=['GET'])
def get_shout():
        verify_request(fetch_key("key_1"), request.headers)
        if request.method == 'GET':
                headers = {'x-api-key': fetch_key("rblx_group_api")}
                return http_get(headers, 'https://apis.roblox.com/cloud/v2/groups/5038001/shout')

@app.route('/status', methods=['GET'])
@limiter.exempt
def status():
        return jsonify({'status': 'OK'}), 200

#@app.route('/test', methods=['GET'])
#def test():
#       return fetch_key("rblx_group_api")

@app.before_request
def before_request():
        if request.headers.get('x-forwarded-proto', '') == 'https':
                request.environ['wsgi.url_scheme'] = 'https'

@app.errorhandler(404)
def page_not_found(e):
        app.logger.warning(f'Attempt to access invalid route {request.path} by {request.headers.get("x-forwarded-for")}')
        return jsonify({'error': 'Unknown route'}), 404

@app.errorhandler(DatabaseConnectionException)
def db_error(e):
        app.logger.warning(f'API connection refused due to internal database error: {str(e)}')
        return jsonify({'error': 'Internal database error'}), 500

@app.errorhandler(UnauthorizedException)
def unauthorized(e):
        response = {'error': 'Resource Unauthorized'}
        return jsonify(response), 401

@app.errorhandler(429)
def rate_limit(e):
        app.logger.warning(f'Rate limit exceeded!')
        return jsonify({'error': 'Rate limit exceeded'}), 429

if __name__ == '__main__':
        app.run(debug=False, host='192.168.100.30')