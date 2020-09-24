import asyncpg
import datetime
import uuid


def converter(data):
    if (isinstance(data, asyncpg.Record)):
        dataDict = dict(data)
        for key in dataDict:
            field = dataDict[key]
            if (isinstance(field, datetime.datetime)):
                dataDict[key] = field.isoformat()
            if (isinstance(field, uuid.UUID)):
                dataDict[key] = field.__str__()
        return dataDict
    elif (isinstance(data, list)):
        return list(map(lambda x: converter(x), data))
    else:
        return data
