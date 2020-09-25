from sanic import Sanic, response
from sanic.response import json
import asyncpg
import datetime
from uuid import UUID
import json_utils
import db

app = Sanic("app")


@app.post("/person")
async def create_person(request):
    async with db.pool.acquire() as conn:
        sql = '''
                    INSERT INTO public.person(
                        name, guid, dt)
                        VALUES ($1, $2, $3);
                '''
        rows = await conn.execute(sql, request.json["name"], request.json["guid"], datetime.datetime.fromisoformat(request.json["dt"]))
        return response.json({}, status=201)


@app.route("/wait")
async def wait(request):
    async with db.pool.acquire() as conn:
        sql = '''
                    SELECT pg_sleep(1); 
                '''
        rows = await conn.fetchrow(sql)
        return response.json(json_utils.converter(rows), status=200)


@app.route("/person")
async def person(request):
    async with db.pool.acquire() as conn:
        sql = '''
                    SELECT * FROM public.person
                    ORDER BY id desc
                    LIMIT 10;
                '''
        rows = await conn.fetch(sql)
        return response.json(json_utils.converter(rows), status=200)


@app.listener('before_server_start')
async def register_db(app, loop):
    await db.connect(loop)


@app.listener('after_server_stop')
async def close_connection(app, loop):
    await db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, access_log=True, debug=True)
