 - [18/Jan/2026:15:40:38 +0000] "GET /health HTTP/1.1" 200 62 "-" "Render/1.0"
10.209.22.76 - - [18/Jan/2026:15:40:42 +0000] "GET /health HTTP/1.1" 200 62 "-" "Render/1.0"
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
pg8000.dbapi.ProgrammingError: {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 282, in handle
    keepalive = self.handle_request(req, conn)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 334, in handle_request
    respiter = self.wsgi(environ, resp.start_response)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2088, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_socketio/__init__.py", line 43, in __call__
    return super(_SocketIOMiddleware, self).__call__(environ,
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
10.21.56.66 - - [18/Jan/2026:15:40:55 +0000] "GET /admin/logs/actions/data?page=1&driver_id=2&action_types=all HTTP/1.1" 500 0 "-" "-"
                                                     start_response)
                                                     ^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/engineio/middleware.py", line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2073, in wsgi_app
    response = self.handle_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2070, in wsgi_app
    response = self.full_dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1515, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1513, in full_dispatch_request
    rv = self.dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1499, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**req.view_args)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_login/utils.py", line 272, in decorated_view
    return func(*args, **kwargs)
  File "/opt/render/project/src/routes/admin.py", line 224, in action_logs_data
    operator_results = operator_query.all()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2644, in all
    return self._iter().all()
           ~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2779, in _iter
    result = self.session.execute(
        statement,
        params,
        execution_options={"_sa_orm_load_options": self.load_options},
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1653, in execute
    result = conn._execute_20(statement, params or {}, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1520, in _execute_20
    return meth(self, args_10style, kwargs_10style, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/sql/elements.py", line 313, in _execute_on_connection
    return connection._execute_clauseelement(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        self, multiparams, params, execution_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1389, in _execute_clauseelement
    ret = self._execute_context(
        dialect,
    ...<8 lines>...
        cache_hit=cache_hit,
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1748, in _execute_context
    self._handle_dbapi_exception(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        e, statement, parameters, cursor, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1929, in _handle_dbapi_exception
    util.raise_(
    ~~~~~~~~~~~^
        sqlalchemy_exception, with_traceback=exc_info[2], from_=e
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/compat.py", line 198, in raise_
    raise exception
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
sqlalchemy.exc.ProgrammingError: (pg8000.dbapi.ProgrammingError) {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
[SQL: SELECT operator_action_logs.id AS operator_action_logs_id, operator_action_logs.operator_id AS operator_action_logs_operator_id, operator_action_logs.action AS operator_action_logs_action, operator_action_logs.target_type AS operator_action_logs_target_type, operator_action_logs.target_id AS operator_action_logs_target_id, operator_action_logs.meta_data AS operator_action_logs_meta_data, operator_action_logs.created_at AS operator_action_logs_created_at, users.username AS operator_username, vehicles.registration_number AS vehicle_registration 
FROM operator_action_logs JOIN users ON operator_action_logs.operator_id = users.id LEFT OUTER JOIN vehicles ON operator_action_logs.target_id = vehicles.id 
WHERE operator_action_logs.target_type = %s AND operator_action_logs.target_id = %s OR json_extract(operator_action_logs.meta_data, %s) = %s]
[parameters: ('driver', 2, '$.driver_id', 2)]
(Background on this error at: http://sqlalche.me/e/14/f405)
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
pg8000.dbapi.ProgrammingError: {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 282, in handle
    keepalive = self.handle_request(req, conn)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 334, in handle_request
    respiter = self.wsgi(environ, resp.start_response)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2088, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_socketio/__init__.py", line 43, in __call__
    return super(_SocketIOMiddleware, self).__call__(environ,
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
10.21.56.66 - - [18/Jan/2026:15:40:55 +0000] "GET /admin/logs/actions/data?page=1&driver_id=2&action_types=all HTTP/1.1" 500 0 "-" "-"
                                                     start_response)
                                                     ^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/engineio/middleware.py", line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2073, in wsgi_app
    response = self.handle_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2070, in wsgi_app
    response = self.full_dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1515, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1513, in full_dispatch_request
    rv = self.dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1499, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**req.view_args)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_login/utils.py", line 272, in decorated_view
    return func(*args, **kwargs)
  File "/opt/render/project/src/routes/admin.py", line 224, in action_logs_data
    operator_results = operator_query.all()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2644, in all
    return self._iter().all()
           ~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2779, in _iter
    result = self.session.execute(
        statement,
        params,
        execution_options={"_sa_orm_load_options": self.load_options},
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1653, in execute
    result = conn._execute_20(statement, params or {}, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1520, in _execute_20
    return meth(self, args_10style, kwargs_10style, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/sql/elements.py", line 313, in _execute_on_connection
    return connection._execute_clauseelement(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        self, multiparams, params, execution_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1389, in _execute_clauseelement
    ret = self._execute_context(
        dialect,
    ...<8 lines>...
        cache_hit=cache_hit,
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1748, in _execute_context
    self._handle_dbapi_exception(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        e, statement, parameters, cursor, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1929, in _handle_dbapi_exception
    util.raise_(
    ~~~~~~~~~~~^
        sqlalchemy_exception, with_traceback=exc_info[2], from_=e
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/compat.py", line 198, in raise_
    raise exception
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
sqlalchemy.exc.ProgrammingError: (pg8000.dbapi.ProgrammingError) {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
[SQL: SELECT operator_action_logs.id AS operator_action_logs_id, operator_action_logs.operator_id AS operator_action_logs_operator_id, operator_action_logs.action AS operator_action_logs_action, operator_action_logs.target_type AS operator_action_logs_target_type, operator_action_logs.target_id AS operator_action_logs_target_id, operator_action_logs.meta_data AS operator_action_logs_meta_data, operator_action_logs.created_at AS operator_action_logs_created_at, users.username AS operator_username, vehicles.registration_number AS vehicle_registration 
FROM operator_action_logs JOIN users ON operator_action_logs.operator_id = users.id LEFT OUTER JOIN vehicles ON operator_action_logs.target_id = vehicles.id 
WHERE operator_action_logs.target_type = %s AND operator_action_logs.target_id = %s OR json_extract(operator_action_logs.meta_data, %s) = %s]
[parameters: ('driver', 2, '$.driver_id', 2)]
(Background on this error at: http://sqlalche.me/e/14/f405)
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
pg8000.dbapi.ProgrammingError: {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 282, in handle
    keepalive = self.handle_request(req, conn)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 334, in handle_request
    respiter = self.wsgi(environ, resp.start_response)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2088, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_socketio/__init__.py", line 43, in __call__
    return super(_SocketIOMiddleware, self).__call__(environ,
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
10.21.56.66 - - [18/Jan/2026:15:40:55 +0000] "GET /admin/logs/actions/data?page=1&driver_id=2&action_types=all HTTP/1.1" 500 0 "-" "-"
                                                     start_response)
                                                     ^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/engineio/middleware.py", line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2073, in wsgi_app
    response = self.handle_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2070, in wsgi_app
    response = self.full_dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1515, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1513, in full_dispatch_request
    rv = self.dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1499, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**req.view_args)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_login/utils.py", line 272, in decorated_view
    return func(*args, **kwargs)
  File "/opt/render/project/src/routes/admin.py", line 224, in action_logs_data
    operator_results = operator_query.all()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2644, in all
    return self._iter().all()
           ~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2779, in _iter
    result = self.session.execute(
        statement,
        params,
        execution_options={"_sa_orm_load_options": self.load_options},
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1653, in execute
    result = conn._execute_20(statement, params or {}, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1520, in _execute_20
    return meth(self, args_10style, kwargs_10style, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/sql/elements.py", line 313, in _execute_on_connection
    return connection._execute_clauseelement(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        self, multiparams, params, execution_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1389, in _execute_clauseelement
    ret = self._execute_context(
        dialect,
    ...<8 lines>...
        cache_hit=cache_hit,
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1748, in _execute_context
    self._handle_dbapi_exception(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        e, statement, parameters, cursor, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1929, in _handle_dbapi_exception
    util.raise_(
    ~~~~~~~~~~~^
        sqlalchemy_exception, with_traceback=exc_info[2], from_=e
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/compat.py", line 198, in raise_
    raise exception
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
sqlalchemy.exc.ProgrammingError: (pg8000.dbapi.ProgrammingError) {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
[SQL: SELECT operator_action_logs.id AS operator_action_logs_id, operator_action_logs.operator_id AS operator_action_logs_operator_id, operator_action_logs.action AS operator_action_logs_action, operator_action_logs.target_type AS operator_action_logs_target_type, operator_action_logs.target_id AS operator_action_logs_target_id, operator_action_logs.meta_data AS operator_action_logs_meta_data, operator_action_logs.created_at AS operator_action_logs_created_at, users.username AS operator_username, vehicles.registration_number AS vehicle_registration 
FROM operator_action_logs JOIN users ON operator_action_logs.operator_id = users.id LEFT OUTER JOIN vehicles ON operator_action_logs.target_id = vehicles.id 
WHERE operator_action_logs.target_type = %s AND operator_action_logs.target_id = %s OR json_extract(operator_action_logs.meta_data, %s) = %s]
[parameters: ('driver', 2, '$.driver_id', 2)]
(Background on this error at: http://sqlalche.me/e/14/f405)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
pg8000.dbapi.ProgrammingError: {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 282, in handle
    keepalive = self.handle_request(req, conn)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 334, in handle_request
    respiter = self.wsgi(environ, resp.start_response)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2088, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_socketio/__init__.py", line 43, in __call__
    return super(_SocketIOMiddleware, self).__call__(environ,
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
10.21.56.66 - - [18/Jan/2026:15:40:55 +0000] "GET /admin/logs/actions/data?page=1&driver_id=2&action_types=all HTTP/1.1" 500 0 "-" "-"
                                                     start_response)
                                                     ^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/engineio/middleware.py", line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2073, in wsgi_app
    response = self.handle_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2070, in wsgi_app
    response = self.full_dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1515, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1513, in full_dispatch_request
    rv = self.dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1499, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**req.view_args)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_login/utils.py", line 272, in decorated_view
    return func(*args, **kwargs)
  File "/opt/render/project/src/routes/admin.py", line 224, in action_logs_data
    operator_results = operator_query.all()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2644, in all
    return self._iter().all()
           ~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2779, in _iter
    result = self.session.execute(
        statement,
        params,
        execution_options={"_sa_orm_load_options": self.load_options},
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1653, in execute
    result = conn._execute_20(statement, params or {}, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1520, in _execute_20
    return meth(self, args_10style, kwargs_10style, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/sql/elements.py", line 313, in _execute_on_connection
    return connection._execute_clauseelement(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        self, multiparams, params, execution_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1389, in _execute_clauseelement
    ret = self._execute_context(
        dialect,
    ...<8 lines>...
        cache_hit=cache_hit,
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1748, in _execute_context
    self._handle_dbapi_exception(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        e, statement, parameters, cursor, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1929, in _handle_dbapi_exception
    util.raise_(
    ~~~~~~~~~~~^
        sqlalchemy_exception, with_traceback=exc_info[2], from_=e
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/compat.py", line 198, in raise_
    raise exception
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
sqlalchemy.exc.ProgrammingError: (pg8000.dbapi.ProgrammingError) {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
[SQL: SELECT operator_action_logs.id AS operator_action_logs_id, operator_action_logs.operator_id AS operator_action_logs_operator_id, operator_action_logs.action AS operator_action_logs_action, operator_action_logs.target_type AS operator_action_logs_target_type, operator_action_logs.target_id AS operator_action_logs_target_id, operator_action_logs.meta_data AS operator_action_logs_meta_data, operator_action_logs.created_at AS operator_action_logs_created_at, users.username AS operator_username, vehicles.registration_number AS vehicle_registration 
FROM operator_action_logs JOIN users ON operator_action_logs.operator_id = users.id LEFT OUTER JOIN vehicles ON operator_action_logs.target_id = vehicles.id 
WHERE operator_action_logs.target_type = %s AND operator_action_logs.target_id = %s OR json_extract(operator_action_logs.meta_data, %s) = %s]
[parameters: ('driver', 2, '$.driver_id', 2)]
(Background on this error at: http://sqlalche.me/e/14/f405)
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
pg8000.dbapi.ProgrammingError: {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 282, in handle
    keepalive = self.handle_request(req, conn)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 334, in handle_request
    respiter = self.wsgi(environ, resp.start_response)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2088, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_socketio/__init__.py", line 43, in __call__
    return super(_SocketIOMiddleware, self).__call__(environ,
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
10.21.56.66 - - [18/Jan/2026:15:40:55 +0000] "GET /admin/logs/actions/data?page=1&driver_id=2&action_types=all HTTP/1.1" 500 0 "-" "-"
                                                     start_response)
                                                     ^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/engineio/middleware.py", line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2073, in wsgi_app
    response = self.handle_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2070, in wsgi_app
    response = self.full_dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1515, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1513, in full_dispatch_request
    rv = self.dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1499, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**req.view_args)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_login/utils.py", line 272, in decorated_view
    return func(*args, **kwargs)
  File "/opt/render/project/src/routes/admin.py", line 224, in action_logs_data
    operator_results = operator_query.all()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2644, in all
    return self._iter().all()
           ~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2779, in _iter
    result = self.session.execute(
        statement,
        params,
        execution_options={"_sa_orm_load_options": self.load_options},
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1653, in execute
    result = conn._execute_20(statement, params or {}, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1520, in _execute_20
    return meth(self, args_10style, kwargs_10style, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/sql/elements.py", line 313, in _execute_on_connection
    return connection._execute_clauseelement(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        self, multiparams, params, execution_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1389, in _execute_clauseelement
    ret = self._execute_context(
        dialect,
    ...<8 lines>...
        cache_hit=cache_hit,
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1748, in _execute_context
    self._handle_dbapi_exception(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        e, statement, parameters, cursor, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1929, in _handle_dbapi_exception
    util.raise_(
    ~~~~~~~~~~~^
        sqlalchemy_exception, with_traceback=exc_info[2], from_=e
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/compat.py", line 198, in raise_
    raise exception
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
sqlalchemy.exc.ProgrammingError: (pg8000.dbapi.ProgrammingError) {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
[SQL: SELECT operator_action_logs.id AS operator_action_logs_id, operator_action_logs.operator_id AS operator_action_logs_operator_id, operator_action_logs.action AS operator_action_logs_action, operator_action_logs.target_type AS operator_action_logs_target_type, operator_action_logs.target_id AS operator_action_logs_target_id, operator_action_logs.meta_data AS operator_action_logs_meta_data, operator_action_logs.created_at AS operator_action_logs_created_at, users.username AS operator_username, vehicles.registration_number AS vehicle_registration 
FROM operator_action_logs JOIN users ON operator_action_logs.operator_id = users.id LEFT OUTER JOIN vehicles ON operator_action_logs.target_id = vehicles.id 
WHERE operator_action_logs.target_type = %s AND operator_action_logs.target_id = %s OR json_extract(operator_action_logs.meta_data, %s) = %s]
[parameters: ('driver', 2, '$.driver_id', 2)]
(Background on this error at: http://sqlalche.me/e/14/f405)
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
pg8000.dbapi.ProgrammingError: {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 282, in handle
    keepalive = self.handle_request(req, conn)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 334, in handle_request
    respiter = self.wsgi(environ, resp.start_response)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2088, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_socketio/__init__.py", line 43, in __call__
    return super(_SocketIOMiddleware, self).__call__(environ,
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
10.21.56.66 - - [18/Jan/2026:15:40:55 +0000] "GET /admin/logs/actions/data?page=1&driver_id=2&action_types=all HTTP/1.1" 500 0 "-" "-"
                                                     start_response)
                                                     ^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/engineio/middleware.py", line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2073, in wsgi_app
    response = self.handle_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2070, in wsgi_app
    response = self.full_dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1515, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1513, in full_dispatch_request
    rv = self.dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1499, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**req.view_args)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_login/utils.py", line 272, in decorated_view
    return func(*args, **kwargs)
  File "/opt/render/project/src/routes/admin.py", line 224, in action_logs_data
    operator_results = operator_query.all()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2644, in all
    return self._iter().all()
           ~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2779, in _iter
    result = self.session.execute(
        statement,
        params,
        execution_options={"_sa_orm_load_options": self.load_options},
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1653, in execute
    result = conn._execute_20(statement, params or {}, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1520, in _execute_20
    return meth(self, args_10style, kwargs_10style, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/sql/elements.py", line 313, in _execute_on_connection
    return connection._execute_clauseelement(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        self, multiparams, params, execution_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1389, in _execute_clauseelement
    ret = self._execute_context(
        dialect,
    ...<8 lines>...
        cache_hit=cache_hit,
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1748, in _execute_context
    self._handle_dbapi_exception(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        e, statement, parameters, cursor, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1929, in _handle_dbapi_exception
    util.raise_(
    ~~~~~~~~~~~^
        sqlalchemy_exception, with_traceback=exc_info[2], from_=e
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/compat.py", line 198, in raise_
    raise exception
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
sqlalchemy.exc.ProgrammingError: (pg8000.dbapi.ProgrammingError) {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
[SQL: SELECT operator_action_logs.id AS operator_action_logs_id, operator_action_logs.operator_id AS operator_action_logs_operator_id, operator_action_logs.action AS operator_action_logs_action, operator_action_logs.target_type AS operator_action_logs_target_type, operator_action_logs.target_id AS operator_action_logs_target_id, operator_action_logs.meta_data AS operator_action_logs_meta_data, operator_action_logs.created_at AS operator_action_logs_created_at, users.username AS operator_username, vehicles.registration_number AS vehicle_registration 
FROM operator_action_logs JOIN users ON operator_action_logs.operator_id = users.id LEFT OUTER JOIN vehicles ON operator_action_logs.target_id = vehicles.id 
WHERE operator_action_logs.target_type = %s AND operator_action_logs.target_id = %s OR json_extract(operator_action_logs.meta_data, %s) = %s]
[parameters: ('driver', 2, '$.driver_id', 2)]
(Background on this error at: http://sqlalche.me/e/14/f405)
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
pg8000.dbapi.ProgrammingError: {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 282, in handle
    keepalive = self.handle_request(req, conn)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 334, in handle_request
    respiter = self.wsgi(environ, resp.start_response)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2088, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_socketio/__init__.py", line 43, in __call__
    return super(_SocketIOMiddleware, self).__call__(environ,
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
10.21.56.66 - - [18/Jan/2026:15:40:55 +0000] "GET /admin/logs/actions/data?page=1&driver_id=2&action_types=all HTTP/1.1" 500 0 "-" "-"
                                                     start_response)
                                                     ^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/engineio/middleware.py", line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2073, in wsgi_app
    response = self.handle_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2070, in wsgi_app
    response = self.full_dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1515, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1513, in full_dispatch_request
    rv = self.dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1499, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**req.view_args)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_login/utils.py", line 272, in decorated_view
    return func(*args, **kwargs)
  File "/opt/render/project/src/routes/admin.py", line 224, in action_logs_data
    operator_results = operator_query.all()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2644, in all
    return self._iter().all()
           ~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2779, in _iter
    result = self.session.execute(
        statement,
        params,
        execution_options={"_sa_orm_load_options": self.load_options},
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1653, in execute
    result = conn._execute_20(statement, params or {}, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1520, in _execute_20
    return meth(self, args_10style, kwargs_10style, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/sql/elements.py", line 313, in _execute_on_connection
    return connection._execute_clauseelement(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        self, multiparams, params, execution_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1389, in _execute_clauseelement
    ret = self._execute_context(
        dialect,
    ...<8 lines>...
        cache_hit=cache_hit,
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1748, in _execute_context
    self._handle_dbapi_exception(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        e, statement, parameters, cursor, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1929, in _handle_dbapi_exception
    util.raise_(
    ~~~~~~~~~~~^
        sqlalchemy_exception, with_traceback=exc_info[2], from_=e
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/compat.py", line 198, in raise_
    raise exception
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
sqlalchemy.exc.ProgrammingError: (pg8000.dbapi.ProgrammingError) {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
[SQL: SELECT operator_action_logs.id AS operator_action_logs_id, operator_action_logs.operator_id AS operator_action_logs_operator_id, operator_action_logs.action AS operator_action_logs_action, operator_action_logs.target_type AS operator_action_logs_target_type, operator_action_logs.target_id AS operator_action_logs_target_id, operator_action_logs.meta_data AS operator_action_logs_meta_data, operator_action_logs.created_at AS operator_action_logs_created_at, users.username AS operator_username, vehicles.registration_number AS vehicle_registration 
FROM operator_action_logs JOIN users ON operator_action_logs.operator_id = users.id LEFT OUTER JOIN vehicles ON operator_action_logs.target_id = vehicles.id 
WHERE operator_action_logs.target_type = %s AND operator_action_logs.target_id = %s OR json_extract(operator_action_logs.meta_data, %s) = %s]
[parameters: ('driver', 2, '$.driver_id', 2)]
(Background on this error at: http://sqlalche.me/e/14/f405)
[2026-01-18 15:40:55 +0000] [64] [ERROR] Error handling request /admin/logs/actions/data?page=1&driver_id=2&action_types=all
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 254, in execute
    self._context = self._c.execute_unnamed(
                    ~~~~~~~~~~~~~~~~~~~~~~~^
        statement, vals=vals, oids=self._input_oids, stream=stream
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 688, in execute_unnamed
    self.handle_messages(context)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 827, in handle_messages
    raise context.error
pg8000.exceptions.DatabaseError: {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
pg8000.dbapi.ProgrammingError: {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 282, in handle
    keepalive = self.handle_request(req, conn)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/gunicorn/workers/gthread.py", line 334, in handle_request
    respiter = self.wsgi(environ, resp.start_response)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2088, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_socketio/__init__.py", line 43, in __call__
    return super(_SocketIOMiddleware, self).__call__(environ,
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
10.21.56.66 - - [18/Jan/2026:15:40:55 +0000] "GET /admin/logs/actions/data?page=1&driver_id=2&action_types=all HTTP/1.1" 500 0 "-" "-"
                                                     start_response)
                                                     ^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/engineio/middleware.py", line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2073, in wsgi_app
    response = self.handle_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 2070, in wsgi_app
    response = self.full_dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1515, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_cors/extension.py", line 194, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1513, in full_dispatch_request
    rv = self.dispatch_request()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask/app.py", line 1499, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**req.view_args)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/flask_login/utils.py", line 272, in decorated_view
    return func(*args, **kwargs)
  File "/opt/render/project/src/routes/admin.py", line 224, in action_logs_data
    operator_results = operator_query.all()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2644, in all
    return self._iter().all()
           ~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2779, in _iter
    result = self.session.execute(
        statement,
        params,
        execution_options={"_sa_orm_load_options": self.load_options},
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1653, in execute
    result = conn._execute_20(statement, params or {}, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1520, in _execute_20
    return meth(self, args_10style, kwargs_10style, execution_options)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/sql/elements.py", line 313, in _execute_on_connection
    return connection._execute_clauseelement(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        self, multiparams, params, execution_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1389, in _execute_clauseelement
    ret = self._execute_context(
        dialect,
    ...<8 lines>...
        cache_hit=cache_hit,
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1748, in _execute_context
    self._handle_dbapi_exception(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        e, statement, parameters, cursor, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1929, in _handle_dbapi_exception
    util.raise_(
    ~~~~~~~~~~~^
        sqlalchemy_exception, with_traceback=exc_info[2], from_=e
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/compat.py", line 198, in raise_
    raise exception
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1705, in _execute_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, statement, parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 681, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 281, in execute
    raise cls(msg)
sqlalchemy.exc.ProgrammingError: (pg8000.dbapi.ProgrammingError) {'S': 'ERROR', 'V': 'ERROR', 'C': '42883', 'M': 'function json_extract(json, character varying) does not exist', 'H': 'No function matches the given name and argument types. You might need to add explicit type casts.', 'P': '796', 'F': 'parse_func.c', 'L': '629', 'R': 'ParseFuncOrColumn'}
[SQL: SELECT operator_action_logs.id AS operator_action_logs_id, operator_action_logs.operator_id AS operator_action_logs_operator_id, operator_action_logs.action AS operator_action_logs_action, operator_action_logs.target_type AS operator_action_logs_target_type, operator_action_logs.target_id AS operator_action_logs_target_id, operator_action_logs.meta_data AS operator_action_logs_meta_data, operator_action_logs.created_at AS operator_action_logs_created_at, users.username AS operator_username, vehicles.registration_number AS vehicle_registration 
FROM operator_action_logs JOIN users ON operator_action_logs.operator_id = users.id LEFT OUTER JOIN vehicles ON operator_action_logs.target_id = vehicles.id 
WHERE operator_action_logs.target_type = %s AND operator_action_logs.target_id = %s OR json_extract(operator_action_logs.meta_data, %s) = %s]
[parameters: ('driver', 2, '$.driver_id', 2)]
(Background on this error at: http://sqlalche.me/e/14/f405)
10.209.22.76 - - [18/Jan/2026:15:40:57 +0000] "GET /health HTTP/1.1" 200 62 "-" "Render/1.0"
10.209.27.183 - - [18/Jan/2026:15:40:58 +0000] "GET /health HTTP/1.1" 200 61 "-" "Render/1.0"
10.209.22.76 - - [18/Jan/2026:15:41:02 +0000] "GET /health HTTP/1.1" 200 62 "-" "Render/1.0"
10.209.27.183 - - [18/Jan/2026:15:41:03 +0000] "GET /health HTTP/1.1" 200 62 "-" "Render/1.0"