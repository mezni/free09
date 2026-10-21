
from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.engine import Engine

USER_RECORDS = [
    {"username": "telco.agent.001", "role": "AGENT"},
    {"username": "telco.agent.002", "role": "AGENT"},
    {"username": "telco.supervisor.001", "role": "SUPERVISOR"},
    {"username": "telco.ai.001", "role": "AI_BOT"},
]


def seed_users(engine: Engine) -> int:
    """Insert missing IAM users and return the number inserted."""
    with engine.begin() as connection:
        inspector = inspect(connection)

        if "users" not in inspector.get_table_names(schema="iam"):
            raise RuntimeError(
                "Table iam.users does not exist. Run Alembic migrations first."
            )

        users = Table(
            "users",
            MetaData(),
            schema="iam",
            autoload_with=connection,
        )

        existing = set(
            connection.execute(
                select(users.c.username)
            ).scalars()
        )

        inserted = 0

        for record in USER_RECORDS:
            if record["username"] in existing:
                continue

            connection.execute(users.insert().values(**record))
            existing.add(record["username"])
            inserted += 1

        return inserted

