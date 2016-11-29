"""Functions to fetch and update user profile info."""

from datetime import datetime


def get_user_info(db, user_id, test=False):
    """Fetch user info from database."""
    user_id = int(user_id)
    cur = db.cursor()
    user_info = None
    if test:
        user_info = cur.execute(
            'SELECT * FROM users WHERE user_id=?', (user_id, )).fetchone()
    else:
        cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id, ))
        user_info = cur.fetchone()
    column_names = tuple(description[0] for description in cur.description)
    cur.close()
    if user_info is None:
        return None
    return dict(zip(column_names, user_info))


def update_user(db, user_id, name, email, test=False):
    """Upsert user row in the database."""
    user_id = int(user_id)
    cur = db.cursor()
    existing_user = None
    if test:
        existing_user = cur.execute(
            'SELECT * FROM users WHERE user_id=?', (user_id, )).fetchone()
    else:
        cur.execute(
            "SELECT * FROM users WHERE user_id=%s", (user_id, ))
        existing_user = cur.fetchone()
    if existing_user is None:
        # user doesn't exist: insert
        if test:
            cur.execute(
                'INSERT INTO users (user_id, name, email) VALUES (?, ?, ?)',
                (user_id, name, email))
        else:
            cur.execute(
                "INSERT INTO users (user_id, name, email) VALUES (%s, %s, %s)",
                (user_id, name, email))
        db.commit()
    else:
        # user exists: update
        old_user_id, old_name, old_email = existing_user
        if old_name != name or old_email != email:
            if test:
                cur.execute(
                    'UPDATE users SET name=?, email=? WHERE user_id=?',
                    (name, email, user_id))
            else:
                cur.execute(
                    "UPDATE users SET name=%s, email=%s WHERE user_id=%s",
                    (name, email, user_id))
            db.commit()
    cur.close()


def get_user_location_history(db, user_id, since_timestamp, test=False):
    """Get user's location history after since_timestamp."""
    user_id = int(user_id)
    cur = db.cursor()
    location_history = None
    if test:
        location_history = cur.execute(
            'SELECT * FROM location_history WHERE user_id=? AND timestamp>=?',
            (user_id, since_timestamp)).fetchall()
    else:
        location_history = cur.execute(
            """SELECT * FROM location_history
            WHERE user_id=%s AND timestamp>=%s""",
            (user_id, since_timestamp)).fetchall()
        location_history = cur.fetchall()
    column_names = tuple(description[0] for description in cur.description)
    cur.close()
    return map(lambda entry: dict(zip(column_names, entry)), location_history)


def update_user_location_history(db, user_id, place_id, test=False):
    """Insert new location history entry for a given user."""
    user_id = int(user_id)
    cur = db.cursor()
    unix_timestamp = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
    if test:
        cur.execute(
            '''INSERT INTO location_history
            (user_id, place_id, timestamp) VALUES (?, ?, ?)''',
            (user_id, place_id, unix_timestamp))
    else:
        cur.execute(
            """INSERT INTO location_history
            (user_id, place_id, timestamp) VALUES (%s, %s, %s)""",
            (user_id, place_id, unix_timestamp))
    db.commit()
    cur.close()
