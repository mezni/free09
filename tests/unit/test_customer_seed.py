
from infra.postgres.seed.customers import build_customer_records


def test_customer_records_are_deterministic():
    first_run = build_customer_records(5)
    second_run = build_customer_records(5)

    assert first_run == second_run


def test_customer_records_have_unique_identifiers():
    records = build_customer_records(20)

    numbers = [record["customer_number"] for record in records]
    emails = [record["email"] for record in records]

    assert len(numbers) == len(set(numbers))
    assert len(emails) == len(set(emails))


def test_customer_records_match_database_constraints():
    records = build_customer_records(20)

    allowed_statuses = {"ACTIVE", "INACTIVE", "SUSPENDED"}

    for record in records:
        assert len(record["customer_number"]) <= 30
        assert len(record["first_name"]) <= 100
        assert len(record["last_name"]) <= 100
        assert len(record["email"]) <= 254
        assert len(record["phone"]) <= 30
        assert record["status"] in allowed_statuses
        assert record["email"].endswith("@example.test")

