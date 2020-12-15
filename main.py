from sanic import Sanic, response
from sanic.response import json
import asyncpg
import datetime
from uuid import UUID
import json_utils
import db

app = Sanic("app")


@app.route('/person/<person_id>', methods=['PUT'])
async def post_handler(request, person_id):
    async with db.pool.acquire() as conn:
        sql = '''
                UPDATE public.person
                SET name=COALESCE($1,name), guid=COALESCE($2,guid), dt=COALESCE($3,dt)
                WHERE id = $4
                '''
        dt_value = request.json.get("dt", None)
        dt = None if dt_value == None else datetime.datetime.fromisoformat(
            dt_value)
        rows = await conn.execute(sql, request.json.get("name", None), request.json.get("guid", None), dt, int(person_id))
        return response.json(request.json, status=200)


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


@app.route("/person")
async def person(request):
    params = dict(request.query_args)
    name = params.get('name', None)
    if name != None:
        name = '%{}%'.format(name)
    async with db.pool.acquire() as conn:
        sql = '''
                    SELECT * FROM public.person
                    WHERE ( $1::varchar IS NULL OR name ILIKE $1::varchar )
                    ORDER BY id desc
                    LIMIT 10;
                '''
        rows = await conn.fetch(sql, name)
        return response.json(json_utils.converter(rows), status=200)


@app.listener('before_server_start')
async def register_db(app, loop):
    await db.connect(loop)


@app.listener('after_server_stop')
async def close_connection(app, loop):
    await db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, access_log=True, debug=True)
