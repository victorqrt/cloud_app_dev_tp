#!/bin/bash

TABLES=(awards_players players_teams coaches draft series_post teams_post teams players)

for t in ${TABLES[@]}; do
    echo "[ ] Pushing table $t to mongoDB cluster as a new collection..."
    mongoimport --host CloudMLVQ-shard-0/cloudmlvq-shard-00-00-r4zfj.mongodb.net:27017,cloudmlvq-shard-00-01-r4zfj.mongodb.net:27017,cloudmlvq-shard-00-02-r4zfj.mongodb.net:27017 --ssl --username Gentoo --password installgentoo --authenticationDatabase admin --db imports --collection $t --type CSV --file $t.csv --headerline
done

echo "[+] Done."
