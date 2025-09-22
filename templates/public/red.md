# README — Render performance diagnosis

**Project:** drive-monitoring-iha2.onrender.com
**Issue:** High TTFB on warm requests (observed \~15–26s). Problem appears at the origin (Gunicorn app / DB / request path), not DNS/TLS.

---

## 1) Quick summary

* Network/TLS to Cloudflare + Render is fast.
* `curl` timing shows `starttransfer` (TTFB) ≈ **26.59s** for a GET to `/` — server-side processing delay.
* Most likely root causes: DB connection overhead, blocking work in request handlers, or Gunicorn worker misconfiguration.

---

## 2) Key measurements (from troubleshooting)

```
# HEAD request shows Cloudflare + gunicorn origin
curl -I -v https://drive-monitoring-iha2.onrender.com/
# GET timing breakdown (example output)
namelookup=0.007116s connect=0.250020s appconnect=0.439643s pretransfer=0.439708s starttransfer=26.588903s total=26.593562s
# earlier single GET showed ttfb ~15.77s also (warm but slow)
ttfb=15.772764s total=15.781700s
```

---

## 3) Repro steps (commands to run locally)

1. Re-run the timing breakdown:

```bash
curl -o /dev/null -s -w "namelookup=%{time_namelookup}s connect=%{time_connect}s appconnect=%{time_appconnect}s pretransfer=%{time_pretransfer}s starttransfer=%{time_starttransfer}s total=%{time_total}s\n" https://drive-monitoring-iha2.onrender.com/
```

2. Add two endpoints (see section 4), redeploy, then measure each:

```bash
curl -o /dev/null -s -w "ttfb=%{time_starttransfer}s total=%{time_total}s\n" https://drive-monitoring-iha2.onrender.com/ping
curl -o /dev/null -s -w "ttfb=%{time_starttransfer}s total=%{time_total}s\n" https://drive-monitoring-iha2.onrender.com/db-ping
```

---

## 4) Endpoints to add (copy-paste)

### Node / Express

```js
// /ping
app.get('/ping', (req, res) => res.status(200).send('pong'));

// /db-ping (adjust to your DB client)
app.get('/db-ping', async (req, res) => {
  const t0 = Date.now();
  await pool.query('SELECT 1');
  res.json({ ok: true, took_ms: Date.now() - t0 });
});
```

### Python / Flask

```py
@app.route('/ping')
def ping():
    return 'pong', 200

@app.route('/db-ping')
def db_ping():
    import time
    t0 = time.time()
    cur = db_conn.cursor(); cur.execute('SELECT 1'); cur.fetchall()
    return {'took_ms': int((time.time()-t0)*1000)}
```

---

## 5) Interpretation guide

* `/ping` fast, `/db-ping` slow → **DB is culprit** (connection overhead or slow query).
* Both `/ping` and `/db-ping` slow → **app/Gunicorn startup or per-request initialization** or blocking work in handler.

---

## 6) Immediate recommended actions (priority order)

1. **DB pooling / persistent connections**

   * Node: `pg.Pool` or mysql pooling
   * Python: SQLAlchemy/psycopg2 pool or add **PgBouncer** if using Postgres
2. **Offload heavy work** to background workers (Redis + Celery/RQ for Python; Bull/BullMQ for Node). Webhooks should return `200` immediately and enqueue processing.
3. **Tune Gunicorn**

   * Suggested example for blocking I/O apps:

     ```bash
     gunicorn -w 3 -k gthread --threads 4 --timeout 30 app:app --access-logfile - --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'
     ```
   * Use `workers ≈ 2 * CPU + 1`.
   * For async frameworks use `uvicorn.workers.UvicornWorker`.
4. **Instrument request path** with timestamps and enable access logs (`%(L)s`) to capture real request durations.
5. **Profile** the app (pyinstrument/py-spy for Python; clinic/0x for Node) if the above don't isolate the issue.

---

## 7) Quick checklist for immediate debugging

* [ ] Add `/ping` and `/db-ping` endpoints and measure TTFB for both.
* [ ] Enable access logs with request duration in Gunicorn.
* [ ] Add timestamp logs around DB and external API calls.
* [ ] If DB is slow: implement pooling or PgBouncer.
* [ ] If handlers block: offload to background worker.
* [ ] Consider Render Starter plan to avoid sleep (note: won't fix warm TTFB by itself).

---

## 8) Notes & follow-ups

* Upgrading to Render Starter (\$7) prevents sleep/cold-starts but **won't** fix warm TTFB if root cause is DB or blocking handlers.
* When you have the `/ping` and `/db-ping` results, paste them in an issue or share here and include a couple of slow request log lines from Render — that will let the next step be pinpointed precisely.

---

*End of README*
