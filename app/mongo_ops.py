from pymongo import MongoClient
from bson.json_util import dumps, loads
from bson.objectid import ObjectId

class MongoOps:

    def __init__(self):
        # Auth in clear because who cares :|
        # The db build is automated (see ../run) and the user has no high privileges anyway
        self.client = MongoClient("mongodb+srv://Gentoo:installgentoo@cloudmlvq-r4zfj.mongodb.net/")

        if "data" not in self.client.list_database_names():
            # Actual conversion to a nosql schema happens now
            print("[ ] First run: preparing the database (may take some time)...")

            print("    [ ] Creating data.teams from the imports...")

            # New collection: data.teams
            # We add to each document:
            #   - The team ID as string field, and all the team variants (by year) as a list
            #   - To each of those variants, the coach document if found
            #   - To each of those variants, the players roster

            teams = list(self.client["imports"]["teams"].find())
            all_teamIDs = set(map(lambda x: x["tmID"], teams))
            coaches = list(self.client["imports"]["coaches"].find())

            self.client["data"]["teams"].insert_many(
                map(
                    lambda _id: {
                        "team_id": _id,

                        # We want to add to the team document the embedded coach document

                        "variants_by_year": list(map(

                            # The update method on python dicts has a none return value, hence the "or e" to effectively return e after
                            # modification. Not very functionnal as we embed a side effect (we're modifying e by reference), but works.

                            lambda e: e.update(
                                {"coach": list(filter(lambda _e: _e["tmID"] == e["tmID"] and _e["year"] == e["year"], coaches))[0]}
                            ) or e,
                            list(filter(lambda x: x["tmID"] == _id, teams))
                        ))
                    },
                    all_teamIDs
                )
            )

            # Let's now add the player roster to each team variant
            # We break this apart from variant creation for simplicity

            print("    [ ] Creating data.players from the imports...")

            # New collection: data.players
            # We add to each player's document:
            #   - A list of the teams she has played on
            #   - A list of her awards

            players = list(self.client["imports"]["players"].find())
            players_teams = list(self.client["imports"]["players_teams"].find()) # To map player to team variant based on team ID and year
            all_playerIDs = set(map(lambda x: x["playerID"], players_teams))

            self.client["data"]["players"].insert_many(players)

            for _id in all_playerIDs:
                self.client["data"]["players"].update_one(
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
                )

            print("[+] Done, starting the webapp.")

    ###########
    # Queries #
    ###########

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

    # 2
    def coach_history(self, coach):
        try:
            return list(
                self.client["data"]["teams"].aggregate([
                    {
                        "$unwind": "$variants_by_year"
                    },
                    {
                        "$match": {
                            "variants_by_year.coach.coachID": coach
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "teamID": "$variants_by_year.coach.tmID",
                            "year": "$variants_by_year.coach.year"
                        }
                    },
                    {
                        "$sort": {
                            "year": 1
                        }
                    }
                ])
            )

        except:
            return []

    # 3
    def player_had_coaches(self, player):
        try:
            return list(
                self.client["data"]["players"].aggregate([
                    {
                        "$match": {
                            "bioID": player
                        }
                    },
                    {
                        "$unwind": "$teams"
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "teamID": "$teams.tmID",
                            "coachID": "$teams.coach.coachID",
                            "year": "$teams.year"
                        }
                    },
                    {
                        "$sort": {
                            "year": 1
                        }
                    }
                ])
            )

        except:
            return []

    # 4
    def team_year_players_had_awards(self, team, year):
        try:
            return list(
                self.client["data"]["teams"].aggregate([
                    {
                        "$unwind": "$variants_by_year"
                    },
                    {
                        "$match": {
                            "variants_by_year.year": year,
                            "variants_by_year.team": team
                        }
                    }
                ])
            )

        except:
            return []

# Flask cannot serialize "ObjectID" type fields, so we recursively stringify them
def deserialize_oids(document):
    if isinstance(document, list):
        for e in document:
            deserialize_oids(e)

    elif isinstance(document, dict):
        if "_id" in document:
            document["_id"] = str(document["_id"])
        for k,v in document.items():
            deserialize_oids(v)

    return document
