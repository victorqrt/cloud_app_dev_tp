from pymongo import MongoClient
from bson.json_util import dumps, loads, RELAXED_JSON_OPTIONS

class MongoOps:

    def __init__(self):
        # Auth in clear because who cares :|
        # The db build is automated anyway ( see ../scripts)
        self.client = MongoClient("mongodb+srv://Gentoo:installgentoo@cloudmlvq-r4zfj.mongodb.net/test")

    def get_db_colls(self, db):
        return self.client[db].collection_names()

    def get_raw_coll(self, db, coll):
        res = list(self.client[db][coll].find())
        for e in res:
            e.pop("_id")
        return res
