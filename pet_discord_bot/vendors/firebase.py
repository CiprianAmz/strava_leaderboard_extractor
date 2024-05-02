import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


class FirebaseClient:
    def __init__(self, db_url, db_table, credential_path):
        self.cred = credentials.Certificate(credential_path)
        self.initialized_app = firebase_admin.initialize_app(self.cred, {
            'databaseURL': db_url
        })
        self.db_ref = db.reference("/" + db_table)

    def fetch_all(self):
        """Fetches all entities from Firebase."""
        return self.db_ref.get()

    def update_score(self, user_id, score):
        """Updates the score for a given user."""
        self.db_ref.child(user_id).set(score)

    def close(self):
        """Cleanly closes the Firebase app."""
        firebase_admin.delete_app(self.initialized_app)
