from pymongo import MongoClient
from bson.json_util import dumps, loads
from bson.objectid import ObjectId

class MongoOps:

    def __init__(self):
        # Auth in clear because who cares :|
        # The db build is automated anyway (see ../run)
        self.client = MongoClient("mongodb+srv://Gentoo:installgentoo@cloudmlvq-r4zfj.mongodb.net/test")

        if "data" not in self.client.list_database_names(): # Actual conversion to a nosql schema happens now
            print("[ ] First run: preparing the database...")

            # New collection: data.teams
            # Each document has the team ID as string field, and all the team characteristics (by year) as a list
            teams = list(self.client["imports"]["teams"].find())
            all_teamIDs = set(map(lambda x: x["tmID"], teams))

            new_teams = []
            for i in all_teamIDs:
                new_teams.append({
                    "team_id": i,
                    "characteristics": list(filter(lambda x: x["tmID"] == i, teams))
                })

            self.client["data"]["teams"].insert_many(new_teams)

            print("[+] Done, starting the webapp.")

    def get_db_colls(self):
        return self.client["imports"].collection_names()

    def get_raw_coll(self, coll, pop_oid=False):
        res = list(self.client["imports"][coll].find())
        if pop_oid:
            res = deserialize_oids(res)
        return res

    def get_full_players_documents(self):
        return deserialize_oids(
            list(self.client["imports"]["players_teams"].aggregate([{
                "$lookup": {
                    "from": "players",
                    "localField": "playerID",
                    "foreignField": "bioID",
                    "as": "player"
                    }
                }]))
            )

def deserialize_oids(document): # Flask cannot serialize "ObjectID" type fields, so we recursively stringify them
    if isinstance(document, list):
        for e in document:
            deserialize_oids(e)

    elif isinstance(document, dict):
        document["_id"] = str(document["_id"])
        for k,v in document.items():
            deserialize_oids(v)

    return document
