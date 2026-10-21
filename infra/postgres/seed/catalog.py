
from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.engine import Engine


CATALOG_DATA = {
    "products": [
        {
            "code": "MOBILE",
            "name": "Mobile Services",
            "description": "Mobile connectivity services",
        },
        {
            "code": "INTERNET",
            "name": "Internet Services",
            "description": "Residential internet services",
        },
    ],
    "plans": [
        {
            "code": "MOBILE_BASIC",
            "name": "Mobile Basic",
            "description": "Entry-level mobile plan",
        },
        {
            "code": "MOBILE_PREMIUM",
            "name": "Mobile Premium",
            "description": "Premium mobile plan",
        },
    ],
    "addons": [
        {
            "code": "EXTRA_DATA",
            "name": "Extra Data",
            "description": "Additional mobile data",
        },
        {
            "code": "INTL_CALLING",
            "name": "International Calling",
            "description": "International calling package",
        },
    ],
}


def seed_table(
    connection,
    table: Table,
    records: list[dict],
) -> int:
    """Insert missing catalog records using their unique code."""
    columns = {column.name for column in table.columns}

    required = {"code", "name"}
    missing = required - columns

    if missing:
        raise ValueError(
            f"{table.fullname} is missing required columns: "
            f"{sorted(missing)}"
        )

    existing_codes = set(
        connection.execute(
            select(table.c.code)
        ).scalars()
    )

    inserted = 0

    for record in records:
        if record["code"] in existing_codes:
            continue

        payload = {
            key: value
            for key, value in record.items()
            if key in columns
        }

        connection.execute(table.insert().values(**payload))
        existing_codes.add(record["code"])
        inserted += 1

    return inserted


def seed_catalog(engine: Engine) -> dict[str, int]:
    """Seed catalog tables in one transaction."""
    metadata = MetaData()

    with engine.begin() as connection:
        inspector = inspect(connection)
        available_tables = set(
            inspector.get_table_names(schema="catalog")
        )

        expected_tables = set(CATALOG_DATA)
        missing_tables = expected_tables - available_tables

        if missing_tables:
            raise RuntimeError(
                "Missing catalog tables: "
                f"{sorted(missing_tables)}"
            )

        results = {}

        for table_name, records in CATALOG_DATA.items():
            table = Table(
                table_name,
                metadata,
                schema="catalog",
                autoload_with=connection,
            )

            results[table_name] = seed_table(
                connection,
                table,
                records,
            )

    return results

