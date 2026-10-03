import pytest
from app.data import load_seed_data

@pytest.fixture(autouse=True)
def reset_data():
    load_seed_data()