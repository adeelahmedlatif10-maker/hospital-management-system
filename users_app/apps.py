from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users_app'

    def ready(self):
        self.create_default_admin()

    def create_default_admin(self):
        try:
            from django.db import connection
            with connection.cursor() as cursor:

                cursor.execute(
                    "SELECT ROLE_ID FROM ROLES WHERE ROLE_NAME = %s",
                    ['admin']
                )
                role = cursor.fetchone()

                if not role:
                    cursor.execute(
                        "INSERT INTO ROLES (ROLE_NAME) VALUES (%s)",
                        ['admin']
                    )
                    cursor.execute(
                        "SELECT ROLE_ID FROM ROLES WHERE ROLE_NAME = %s",
                        ['admin']
                    )
                    role = cursor.fetchone()

                role_id = role[0]

                cursor.execute(
                    "SELECT 1 FROM USERS WHERE USER_NAME = %s",
                    ['admin']
                )
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO USERS (USER_NAME, USER_PASSWORD, ROLE_ID) VALUES (%s, %s, %s)",
                        ['admin', 'admin123', role_id]
                    )

        except Exception:
            pass