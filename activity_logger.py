from django.db import connection


def log_activity(username, action, details=None):
    """
    Insert a row into ACTIVITY_LOG.
    Call this from any view after a successful add / update / delete.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ACTIVITY_LOG (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    action   TEXT,
                    details  TEXT,
                    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute(
                "INSERT INTO ACTIVITY_LOG (username, action, details) VALUES (%s, %s, %s)",
                [str(username), str(action), str(details) if details else None]
            )
    except Exception:
        pass 
