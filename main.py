from sanic import Sanic, response
from sanic.response import json
import asyncpg
import datetime
from uuid import UUID
import json_utils

app = Sanic("hello_example")


@app.route("/person")
async def person(request):
    pool = request.app.config['pool']
    async with pool.acquire() as conn:
        sql = '''
                    SELECT id, name, guid, dt
                    FROM public.person; 
                '''
        rows = await conn.fetch(sql)
        return response.json(json_utils.converter(rows), status=200)


@app.listener('before_server_start')
async def register_db(app, loop):
    # Create a database connection pool
    print("Connecting to Postgres")
    conn = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        user='postgres', password='example', host='localhost',
        port=5432, database='sanic'
    )
    poll = await asyncpg.create_pool(
        dsn=conn,
        # in bytes
        min_size=1,
        # in bytes
        max_size=10,
        # maximum query
        max_queries=50000,
        # maximum idle times
        max_inactive_connection_lifetime=300,
        loop=loop)
    app.config['pool'] = poll


@app.listener('after_server_stop')
async def close_connection(app, loop):
    pool = app.config['pool']
    await pool.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, access_log=True, debug=True)
