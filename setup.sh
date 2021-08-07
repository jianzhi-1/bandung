python3 -m venv bandung
source bandung/bin/activate
pip3 install -r requirements.txt
sqlite3 db.db "CREATE TABLE contact(userFrom TEXT, userTo TEXT, codeName TEXT);"
sqlite3 message.db "CREATE TABLE tb(date TEXT, userFrom TEXT, userTo TEXT, message TEXT);"