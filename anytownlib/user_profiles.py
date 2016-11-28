"""Functions to fetch and update user profile info."""

from datetime import datetime


def get_user_info(db, user_id):
    """Fetch user info from database."""
    cur = db.cursor()
    user_info = cur.execute(
        'SELECT * FROM users WHERE user_id=?', (user_id, )).fetchone()
    column_names = tuple(description[0] for description in cur.description)
    cur.close()
    if user_info is None:
        return None
    return dict(zip(column_names, user_info))


def update_user(db, user_id, name, email):
    """Upsert user row in the database."""
    cur = db.cursor()
    existing_user = cur.execute(
        'SELECT * FROM users WHERE user_id=?', (user_id, )).fetchone()
    if existing_user is None:
        # user doesn't exist: insert
        cur.execute(
            'INSERT INTO users (user_id, name, email) VALUES (?, ?, ?)',
            (user_id, name, email))
        db.commit()
    else:
        # user exists: update
        old_user_id, old_name, old_email = existing_user
        if old_name != name or old_email != email:
            cur.execute(
                'UPDATE users SET name=?, email=? WHERE user_id=?',
                (name, email, user_id))
            db.commit()
    cur.close()


def get_user_location_history(db, user_id, since_timestamp):
    """Get user's location history after since_timestamp."""
    cur = db.cursor()
    location_history = cur.execute(
        'SELECT * FROM location_history WHERE user_id=? AND timestamp>=?',
        (user_id, since_timestamp)).fetchall()
    column_names = tuple(description[0] for description in cur.description)
    cur.close()
    return map(lambda entry: dict(zip(column_names, entry)), location_history)


def update_user_location_history(db, user_id, place_id):
    """Insert new location history entry for a given user."""
    cur = db.cursor()
    unix_timestamp = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
    cur.execute(
        '''INSERT INTO location_history
        (user_id, place_id, timestamp) VALUES (?, ?, ?)''',
        (user_id, place_id, unix_timestamp))
    db.commit()
    cur.close()
