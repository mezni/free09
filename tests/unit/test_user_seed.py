
from infra.postgres.seed.users import USER_RECORDS


def test_usernames_are_unique():
    usernames = [record["username"] for record in USER_RECORDS]

    assert len(usernames) == len(set(usernames))


def test_user_roles_match_database_constraint():
    allowed_roles = {"AGENT", "SUPERVISOR", "AI_BOT"}

    for record in USER_RECORDS:
        assert record["role"] in allowed_roles
        assert len(record["username"]) <= 100

