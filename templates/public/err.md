:06:16,870 - app - INFO - Models imported successfully
2025-09-12 01:06:17,269 - app - ERROR - Error during model import or table creation: connect() got an unexpected keyword argument 'ssl'
[2025-09-12 01:06:17 +0000] [55] [INFO] Starting gunicorn 21.2.0
[2025-09-12 01:06:17 +0000] [55] [INFO] Listening at: http://0.0.0.0:10000 (55)
[2025-09-12 01:06:17 +0000] [55] [INFO] Using worker: sync
[2025-09-12 01:06:17 +0000] [57] [INFO] Booting worker with pid: 57
127.0.0.1 - - [12/Sep/2025:01:06:17 +0000] "HEAD / HTTP/1.1" 200 0 "-" "Go-http-client/1.1"
     ==> Your service is live 🎉
     ==> 
     ==> ///////////////////////////////////////////////////////////
     ==> 
     ==> Available at your primary URL https://drive-monitoring-iha2.onrender.com
     ==> 
     ==> ///////////////////////////////////////////////////////////
127.0.0.1 - - [12/Sep/2025:01:06:28 +0000] "GET / HTTP/1.1" 200 81622 "-" "Go-http-client/2.0"
127.0.0.1 - - [12/Sep/2025:01:06:34 +0000] "GET /login HTTP/1.1" 200 35850 "https://drive-monitoring-iha2.onrender.com/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
127.0.0.1 - - [12/Sep/2025:01:06:34 +0000] "GET /static/css/main.css HTTP/1.1" 200 0 "https://drive-monitoring-iha2.onrender.com/login" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
127.0.0.1 - - [12/Sep/2025:01:06:34 +0000] "GET /static/js/driver_actions.js HTTP/1.1" 200 0 "https://drive-monitoring-iha2.onrender.com/login" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
2025-09-12 01:07:04,662 - app - ERROR - Exception on /login [POST]
Traceback (most recent call last):
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
  File "/opt/render/project/src/routes/auth.py", line 78, in login
    user = User.query.filter_by(username=admin_user).first()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2695, in first
    return self.limit(1)._iter().first()
           ~~~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2779, in _iter
    result = self.session.execute(
        statement,
        params,
        execution_options={"_sa_orm_load_options": self.load_options},
    )
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1652, in execute
    conn = self._connection_for_bind(bind, close_with_result=True)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 1502, in _connection_for_bind
    return self._transaction._connection_for_bind(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        engine, execution_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 738, in _connection_for_bind
    conn = bind.connect()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 3067, in connect
    return self._connection_cls(self, close_with_result=close_with_result)
           ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 91, in __init__
    else engine.raw_connection()
         ~~~~~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 3146, in raw_connection
    return self._wrap_pool_connect(self.pool.connect, _connection)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 3113, in _wrap_pool_connect
    return fn()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 301, in connect
    return _ConnectionFairy._checkout(self)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 748, in _checkout
    fairy = _ConnectionRecord.checkout(pool)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 419, in checkout
    rec = pool._do_get()
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/impl.py", line 144, in _do_get
    with util.safe_reraise():
         ~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/langhelpers.py", line 70, in __exit__
    compat.raise_(
    ~~~~~~~~~~~~~^
        exc_value,
        ^^^^^^^^^^
        with_traceback=exc_tb,
        ^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/compat.py", line 198, in raise_
    raise exception
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/impl.py", line 142, in _do_get
    return self._create_connection()
           ~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 247, in _create_connection
    return _ConnectionRecord(self)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 362, in __init__
    self.__connect(first_connect_check=True)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 597, in __connect
    with util.safe_reraise():
         ~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/langhelpers.py", line 70, in __exit__
    compat.raise_(
    ~~~~~~~~~~~~~^
        exc_value,
        ^^^^^^^^^^
        with_traceback=exc_tb,
        ^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/util/compat.py", line 198, in raise_
    raise exception
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 592, in __connect
    connection = pool._invoke_creator(self)
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/create.py", line 578, in connect
    return dialect.connect(*cargs, **cparams)
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 548, in connect
    return self.dbapi.connect(*cargs, **cparams)
           ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
TypeError: connect() got an unexpected keyword argument 'ssl'
127.0.0.1 - - [12/Sep/2025:01:07:04 +0000] "POST /login HTTP/1.1" 500 290 "https:/