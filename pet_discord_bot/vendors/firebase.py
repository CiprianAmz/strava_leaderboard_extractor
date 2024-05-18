import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


class FirebaseClient:
    def __init__(self, db_url, credential_path):
        self.cred = credentials.Certificate(credential_path)
        self.initialized_app = firebase_admin.initialize_app(self.cred, {
            'databaseURL': db_url,
        })

    @staticmethod
    def fetch_all(db_table: str) -> object:
        """Fetches all entities from Firebase."""
        return db.reference("/" + db_table).get()

    @staticmethod
    def upsert(db_table: str, internal_id: str, data: object) -> None:
        """Inserts or updates a new entity into Firebase."""
        db.reference("/" + db_table).child(internal_id).set(data)

    @staticmethod
    def delete(db_table: str, internal_id: str) -> None:
        """Deletes an entity from Firebase."""
        db.reference("/" + db_table).child(internal_id).delete()

    @staticmethod
    def backup_to_json(output_file: str) -> None:
        """Downloads the entire Firebase database as a .json backup file."""
        data = db.reference("/").get()
        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def close(self):
        """Cleanly closes the Firebase app."""
        firebase_admin.delete_app(self.initialized_app)
