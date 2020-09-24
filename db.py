import asyncpg

pool = None


async def connect(loop):
    # Create a database connection pool
    print("Connecting to Postgres")
    conn = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        user='postgres', password='example', host='localhost',
        port=5432, database='sanic'
    )
    global pool
    pool = await asyncpg.create_pool(
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


async def close():
    await pool.close()
