import functools
import gzip
from functools import wraps
from io import BytesIO as IO

import jwt
from flask import request, after_this_request, jsonify, current_app


def allow_access(function):
    """
    allow_access decorator that requires a valid permission

    :param function: function parameter
    :return: decorated_function

    """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        """
        allow_access route that requires a valid permission

        :param function: function parameter
        :return: decorated_functon
        """
        token = request.environ.get('HTTP_AUTHORIZATION', None)

        if token is None:
            return jsonify(message="Token is not valid"), 401
        try:
            payload = jwt.decode(
                token,
                current_app.config.get('JWT_SECRET_KEY'),
                algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            return jsonify(message="Token expired"), 401

        except jwt.InvalidTokenError:
            return jsonify(message="Token is not valid"), 401

        except Exception as e:
            return jsonify(message="Nesto ne valja sa tokenom"), 401

        return function(*args, **kwargs)

    return decorated_function


def log_access(log_category_id=None):
    """
    log_core decorator logging on on panel
    :param log_category_id: Log category identifier
    :param new_description: New description
    :return: decorated function

    """

    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            return function(*args, **kwargs)

        return decorated_function

    return decorator


def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if (response.status_code < 200 or
                    response.status_code >= 300 or
                    'Content-Encoding' in response.headers):
                return response
            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb',
                                      fileobj=gzip_buffer)
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func
