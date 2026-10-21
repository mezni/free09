from infra.postgres.seed.users import seed_users
from infra.postgres.seed.customers import seed_customers
from telco_si.database import engine

try:
    print("IAM users inserted:", seed_users(engine))
    print("CRM customers inserted:", seed_customers(engine))
finally:
    engine.dispose()
