from helium import Client


# Session
#
def test_token_auth(client):
    assert client.api_token is not None

    client.api_token = 'test_auth'
    assert client.api_token == 'test_auth'
    assert client.base_url is not None

    # Test api token on creation
    test_client = Client(api_token='test_auth')
    assert test_client.api_token == 'test_auth'


# Client
#
def _test_resources(client, all, find):
    resources = all(client)
    assert len(resources) > 0

    resource = resources[0]
    assert resource.id is not None

    found_resource = find(client, resource.id)
    assert found_resource.id == resource.id


def test_sensors(client):
    _test_resources(client, Client.sensors, Client.sensor)


def test_labels(client):
    _test_resources(client, Client.labels, Client.label)


def test_organization(client):
    org = client.authorized_organization()
    assert org is not None


def test_user(client):
    user = client.authorized_user()
    assert user is not None
