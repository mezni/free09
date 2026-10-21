from infra.postgres.seed.config import SEED, fake


def test_default_seed():
    assert SEED == 42


def test_faker_instance_exists():
    assert fake is not None


def test_faker_uses_canadian_locale():
    assert fake.locales == ["en_CA"]
