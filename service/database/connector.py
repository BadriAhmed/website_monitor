import psycopg2


class DatabaseConnector:

    def __init__(self, database: str, user: str, password: str, host: str, port: str):
        self.connection = psycopg2.connect(database=database, user=user,
                                           password=password, host=host, port=port)

        self.cursor = self.connection.cursor()

    def execute_query(self, query: str):
        self.cursor.execute(query)

    def commit_changes(self):
        self.connection.commit()

    def fetch_one(self) -> tuple:
        return self.cursor.fetchone()

    def fetch_all(self) -> list:
        return self.cursor.fetchall()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.cursor.close()
        self.connection.close()
