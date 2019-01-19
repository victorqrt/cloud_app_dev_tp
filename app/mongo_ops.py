from pymongo import MongoClient
from bson.json_util import dumps, loads
from bson.objectid import ObjectId

class MongoOps:

    def __init__(self):
        # Auth in clear because who cares :|
        # The db build is automated (see ../run) and the user has no high privileges anyway
        self.client = MongoClient("mongodb+srv://Gentoo:installgentoo@cloudmlvq-r4zfj.mongodb.net/")

        if "data" not in self.client.list_database_names(): # Actual conversion to a nosql schema happens now
            print("[ ] First run: preparing the database (may take some time)...")

            # New collection: data.teams
            # Each document has the team ID as string field, and all the team variants (by year) as a list
            print("    [ ] Creating data.teams from the imports...")

            teams = list(self.client["imports"]["teams"].find())
            all_teamIDs = set(map(lambda x: x["tmID"], teams))

            self.client["data"]["teams"].insert_many(
                map(
                    lambda _id: {
                        "team_id": _id,
                        "variants_by_year": list(filter(lambda x: x["tmID"] == _id, teams))
                    },
                    all_teamIDs
                )
            )

            # New collection: data.players
            # Each player has a list of the teams he played on
            print("    [ ] Creating data.players from the imports...")

            players = list(self.client["imports"]["players"].find())
            players_teams = list(self.client["imports"]["players_teams"].find()) # To map player to team variant based on team ID and year
            all_playerIDs = set(map(lambda x: x["playerID"], players_teams))

            self.client["data"]["players"].insert_many(players)

            map(
                lambda _id: self.client["data"]["players"].update_one(
                    {"bioID": _id},
                    {
                        "$set": {
                            "teams": list(
                                map(
                                    lambda x: list(filter(
                                        lambda y: y["tmID"] == x["tmID"] and y["year"] == x["year"],
                                        teams
                                    ))[0],
                                    filter(lambda t: t["playerID"] == _id, players_teams)
                                )
                            )
                        }
                    }
                ),
                all_playerIDs
            )

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

    # The simple queries

    # 1
    def team_playoff_palmares(self, team):
        team_object = self.client["data"]["teams"].find_one({"team_id": team})

        try:
            return deserialize_oids({
                "playoffs_count": len(list(filter(lambda t: t["playoff"] == "Y", team_object["variants_by_year"]))),
                "palmares": list(map(
                    lambda t: {"year": t["year"], "playoff": t["playoff"]},
                    team_object["variants_by_year"]
                ))
            })

        except:
            return []

def deserialize_oids(document): # Flask cannot serialize "ObjectID" type fields, so we recursively stringify them
    if isinstance(document, list):
        for e in document:
            deserialize_oids(e)

    elif isinstance(document, dict):
        if "_id" in document:
            document["_id"] = str(document["_id"])
        for k,v in document.items():
            deserialize_oids(v)

    return document
