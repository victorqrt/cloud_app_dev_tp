from pymongo import MongoClient

client = MongoClient("mongodb+srv://Gentoo:installgentoo@cloudmlvq-r4zfj.mongodb.net/")
print("[ ] Deleting dbs...")
client.drop_database("imports")
client.drop_database("data")
print("[+] Done.")
