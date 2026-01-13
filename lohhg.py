1-13 11:20:16,436 - app - DEBUG - Vehicle positions cache updated with 0 vehicles
2026-01-13 11:20:16,437 - app - DEBUG - Sent vehicle positions to client: ADImLNkGG9W6cxy6AAAB
[2026-01-13 11:20:40 +0000] [61] [INFO] Handling signal: term
[2026-01-13 11:20:40 +0000] [138] [INFO] Worker exiting (pid: 138)
[2026-01-13 11:20:40 +0000] [61] [INFO] Shutting down: Master
[2026-01-13 11:20:47 +0000] [38] [CRITICAL] WORKER TIMEOUT (pid:63)
[2026-01-13 11:20:47 +0000] [63] [INFO] Worker exiting (pid: 63)
[2026-01-13 11:20:48 +0000] [38] [ERROR] Worker (pid:63) was sent SIGKILL! Perhaps out of memory?
[2026-01-13 11:20:48 +0000] [70] [INFO] Booting worker with pid: 70
10.21.161.1 - - [13/Jan/2026:11:20:48 +0000] "GET /login HTTP/1.1" 200 41947 "https://drive-monitoring-xlm2.onrender.com/" "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"
Database error in /vehicles/active: (pg8000.exceptions.InterfaceError) network error
(Background on this error at: http://sqlalche.me/e/14/rvf5)
10.18.117.68 - - [13/Jan/2026:11:20:48 +0000] "GET /public/vehicles/active HTTP/1.1" 200 109 "https://drive-monitoring-xlm2.onrender.com/" "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"
Invalid session Gl7hyvIes7oI3A4nAAAA (further occurrences of this error will be logged with level INFO)
10.21.161.1 - - [13/Jan/2026:11:20:48 +0000] "POST /socket.io/?EIO=4&transport=polling&t=Pkt5SSv&sid=Gl7hyvIes7oI3A4nAAAA HTTP/1.1" 400 17 "https://drive-monitoring-xlm2.onrender.com/" "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"
10.18.10.0 - - [13/Jan/2026:11:20:48 +0000] "GET /socket.io/?EIO=4&transport=polling&t=Pkt5SSw&sid=Gl7hyvIes7oI3A4nAAAA HTTP/1.1" 400 17 "https://drive-monitoring-xlm2.onrender.com/" "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"
10.23.91.196 - - [13/Jan/2026:11:20:48 +0000] "GET /public/vehicles/active HTTP/1.1" 200 56 "https://drive-monitoring-xlm2.onrender.com/" "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"
Exception during reset or similar
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 144, in _flush
    sock.flush()
    ~~~~~~~~~~^^
  File "/opt/render/project/python/Python-3.13.4/lib/python3.13/socket.py", line 737, in write
    return self._sock.send(b)
           ~~~~~~~~~~~~~~~^^^
  File "/opt/render/project/python/Python-3.13.4/lib/python3.13/ssl.py", line 1232, in send
    return self._sslobj.write(data)
           ~~~~~~~~~~~~~~~~~~^^^^^^
ssl.SSLEOFError: EOF occurred in violation of protocol (_ssl.c:2493)
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 663, in _finalize_fairy
    fairy._reset(pool)
    ~~~~~~~~~~~~^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 875, in _reset
    pool._dialect.do_commit(self)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 634, in do_commit
    dbapi_connection.commit()
    ~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 490, in commit
    self.execute_unnamed("commit")
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 687, in execute_unnamed
    _flush(self._sock)
    ~~~~~~^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 146, in _flush
    raise InterfaceError("network error") from e
pg8000.exceptions.InterfaceError: network error
Exception closing connection <pg8000.legacy.Connection object at 0x78c28fc71160>
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 144, in _flush
    sock.flush()
    ~~~~~~~~~~^^
  File "/opt/render/project/python/Python-3.13.4/lib/python3.13/socket.py", line 737, in write
    return self._sock.send(b)
           ~~~~~~~~~~~~~~~^^^
  File "/opt/render/project/python/Python-3.13.4/lib/python3.13/ssl.py", line 1232, in send
    return self._sslobj.write(data)
           ~~~~~~~~~~~~~~~~~~^^^^^^
ssl.SSLEOFError: EOF occurred in violation of protocol (_ssl.c:2493)
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 663, in _finalize_fairy
    fairy._reset(pool)
    ~~~~~~~~~~~~^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 875, in _reset
    pool._dialect.do_commit(self)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 634, in do_commit
    dbapi_connection.commit()
    ~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/legacy.py", line 490, in commit
    self.execute_unnamed("commit")
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 687, in execute_unnamed
    _flush(self._sock)
    ~~~~~~^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 146, in _flush
    raise InterfaceError("network error") from e
pg8000.exceptions.InterfaceError: network error
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 144, in _flush
    sock.flush()
    ~~~~~~~~~~^^
  File "/opt/render/project/python/Python-3.13.4/lib/python3.13/socket.py", line 737, in write
    return self._sock.send(b)
           ~~~~~~~~~~~~~~~^^^
  File "/opt/render/project/python/Python-3.13.4/lib/python3.13/ssl.py", line 1232, in send
    return self._sslobj.write(data)
           ~~~~~~~~~~~~~~~~~~^^^^^^
ssl.SSLEOFError: EOF occurred in violation of protocol (_ssl.c:2493)
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/pool/base.py", line 238, in _close_connection
    self._dialect.do_close(connection)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 637, in do_close
    dbapi_connection.close()
    ~~~~~~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 541, in close
    _flush(self._sock)
    ~~~~~~^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/pg8000/core.py", line 146, in _flush
    raise InterfaceError("network error") from e
pg8000.exceptions.InterfaceError: network error
10.21.161.1 - - [13/Jan/2026:11:20:48 +0000] "GET /static/css/main.css HTTP/1.1" 304 0 "https:/