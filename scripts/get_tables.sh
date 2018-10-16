#!/bin/bash

TABLES=(awards_players players_teams coaches draft series_post teams_post teams players)
CONNECT='mysql -u guest -p'relational' -h relational.fit.cvut.cz -P 3306 -D Basketball_women'

for t in ${TABLES[@]}; do
    echo "[ ] Downloading CSV dump of table $t..."
    $CONNECT -e "select * from $t;" -B | sed "s/'/\'/;s/\t/\",\"/g;s/^/\"/;s/$/\"/;s/\n//g" > $t.csv
done

echo "[+] Done."
