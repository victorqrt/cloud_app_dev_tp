from pymongo import MongoClient
from bson.json_util import dumps, loads
from bson.objectid import ObjectId

class MongoOps:

    def __init__(self):
        # Auth in clear because who cares :|
        # The db build is automated (see ../run) and the user has no high privileges anyway
        self.client = MongoClient("mongodb+srv://Gentoo:installgentoo@cloudmlvq-r4zfj.mongodb.net/")

        ###################################################
        # Actual conversion to a nosql schema happens now #
        ###################################################

        if "data" not in self.client.list_database_names():
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
            players_teams = list(self.client["imports"]["players_teams"].find()) # To map player to team variant based on team ID and year

            self.client["data"]["teams"].insert_many(
                map(
                    lambda _id: {
                        "team_id": _id,

                        # We want to add the coach to the team variant

                        "variants_by_year": list(map(

                            lambda e: e.update(
                                {
                                    # We embed the coach document
                                    "coach": list(filter(lambda _e: _e["tmID"] == e["tmID"] and _e["year"] == e["year"], coaches))[0],

                                    # Now the team roster. We will only store player ids
                                    "player_ids": list(map(
                                        lambda p: p["playerID"],
                                        filter(lambda _e: _e["tmID"] == e["tmID"] and _e["year"] == e["year"], players_teams)
                                    ))
                                }
                            ) or e,
                            # The update method on python dicts has a none return value, hence the "or e" to effectively return e after
                            # modification. Not very functionnal as we embed a side effect (we're modifying e by reference), but works.

                            filter(lambda x: x["tmID"] == _id, teams)
                        ))
                    },
                    all_teamIDs
                )
            )

            print("    [ ] Creating data.players from the imports...")

            # New collection: data.players
            # We add to each player's document:
            #   - A list of the teams she has played on

            players = list(self.client["imports"]["players"].find())
            all_playerIDs = set(map(lambda x: x["playerID"], players_teams))
            awards = list(self.client["imports"]["awards_players"].find())

            self.client["data"]["players"].insert_many(players)

            for _id in all_playerIDs:
                self.client["data"]["players"].update_one(
                    {"bioID": _id},
                    {
                        "$set": {
                            "teams": list(map(
                                lambda x: list(filter(
                                    lambda y: y["tmID"] == x["tmID"] and y["year"] == x["year"],
                                    teams
                                ))[0],
                                filter(lambda t: t["playerID"] == _id, players_teams)
                            ))
                        }
                    }
                )

            # Indexes

            print("    [ ] Creating indexes...")

            self.client["data"]["teams"].create_index("team_id")
            self.client["data"]["players"].create_index("bioID")

            print("[+] Done, starting the webapp.")

    ########################
    # Queries (see report) #
    ########################

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
    def player_playoff_palmares(self, player):

        try:
            return list(
                self.client["data"]["players"].aggregate([
                    {
                        "$unwind": "$teams"
                    },
                    {
                        "$match": {
                            "bioID": player,
                            "teams.playoff": "Y"
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "year": "$teams.year",
                            "name": "$teams.name",
                            "tmID": "$teams.tmID"
                        }
                    }
                ])
            )

        except:
            return []

    # The heavy queries

    # 1
    def coach_all_trained(self, coach):
        try:
            return list(
                self.client["data"]["teams"].aggregate([
                    {
                        "$match": {
                            "variants_by_year.coach.coachID": coach
                        }
                    },
                    {
                        "$unwind": "$variants_by_year"
                    },
                    {
                        "$unwind": "$variants_by_year.player_ids"
                    },
                    {
                        "$lookup": {
                            "from": "players",
                            "localField": "variants_by_year.player_ids",
                            "foreignField": "bioID",
                            "as": "player"
                        }
                    },
                    {
                        "$unwind": "$player"
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "player_id": "$player.bioID",
                            "player_name": "$player.fullGivenName",
                            "year": "$variants_by_year.year",
                            "tmID": "$variants_by_year.tmID",
                            "team": "$variants_by_year.name"
                        }
                    },
                    {
                        "$group": {
                            "_id": "$player_id",
                            "coached": {
                                "$push": { "year": "$year", "team": "$team", "tmID": "$tmID" }
                            }
                        }
                    },
                    {
                        "$sort": {
                            "coached.year": 1,
                        }
                    }
                ])
            )

        except:
            return []

    # 2
    # This one is tested on a regular mongodb server, but cannot work on our atlas cluster (as it's a free-tier one).
    # The code is here but is not mapped to any API endpoint.
    # This is what the mongo shell raises on the cluster:
    #
    # [js] Error: map reduce failed:{
    #       "ok" : 0,
    #       "errmsg" : "CMD_NOT_ALLOWED: mapreduce",
    #       "code" : 8000,
    #       "codeName" : "AtlasError"
    #    }

    def _3points_rate_by_year(self, year):
        try:
            return list(
                self.client["teams"].map_reduce('''
                    function() {
                        var attended = 0;
                        var marked = 0;

                        this.variants_by_year.forEach(
                            function(v) {
                                if(v.year == 1{0}) {
                                    attended += v.d_3pa;
                                    marked += v.d_3pm;
                                }
                            }
                        );

                        emit(attended, marked);
                    },

                    function(k, v) {
                        return v/k;
                    },

                    {out: {inline: 1}}
                '''.format(year)
                )
            )

        except:
            return []

    ##############################################
    # Miscellaneous requests (for the front-end) #
    ##############################################

    def coach_name_id_pairs(self):
        try:
            return list(
                self.client["imports"]["coaches"].aggregate([
                    {
                        "$group": {
                            "_id": { "coach_id": "$coachID", "coach_name": "$fullName" }
                        }
                    }#,
                    #{
                    #    "$project": {
                    #        "_id": 0,
                    #        "coach_id": "$_id",
                    #        "coach_name": "$fullName"
                    #    }
                    #}
                ])
            )

        except:
            return []

# That one is here just in case we want to pass BSON ObjectIds through the API
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
