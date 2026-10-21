
import os
import random

from faker import Faker

SEED = int(os.getenv("SEED", "42"))

random.seed(SEED)

fake = Faker("en_CA")
Faker.seed(SEED)

