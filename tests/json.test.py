import ujson
import datetime

print(ujson.dumps([{"key": datetime.datetime.now().__str__()}, 81, True]))
