
from sqlalchemy import Column, MetaData, String, Table, create_engine

from infra.postgres.seed.catalog import seed_table


def test_seed_table_inserts_missing_records():
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()

    products = Table(
        "products",
        metadata,
        Column("code", String, primary_key=True),
        Column("name", String, nullable=False),
        Column("description", String),
    )

    metadata.create_all(engine)

    records = [
        {
            "code": "MOBILE",
            "name": "Mobile Services",
            "description": "Mobile connectivity",
        }
    ]

    with engine.begin() as connection:
        inserted = seed_table(connection, products, records)
        inserted_again = seed_table(connection, products, records)

    assert inserted == 1
    assert inserted_again == 0

    engine.dispose()


def test_seed_table_rejects_missing_code_column():
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()

    table = Table(
        "products",
        metadata,
        Column("name", String),
    )

    metadata.create_all(engine)

    with engine.begin() as connection:
        try:
            seed_table(connection, table, [])
        except ValueError as exc:
            assert "code" in str(exc)
        else:
            raise AssertionError("Expected ValueError")

    engine.dispose()

