import pytest

from client.client import FFClient
from report.queries import Q_MASTER_DATA

@pytest.fixture(scope="module")
def client():
    return FFClient()

def test_client(client):
    res = client.q(Q_MASTER_DATA, {'reportCode': '87YtrHC16y3bXQGp'}, cache=False)
    pass