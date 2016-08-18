"""Tests for Organization."""

from __future__ import unicode_literals

import pytest


@pytest.fixture
def authorized_organization(client):
    return client.authorized_organization()


def test_organization(authorized_organization):
    assert authorized_organization is not None


def test_users(authorized_organization):
    users = authorized_organization.users()
    assert users is not None
    assert len(users) > 0


def test_metadata(authorized_organization):
    metadata = authorized_organization.metadata()
    assert metadata is not None


def test_timeseries(authorized_organization):
    timeseries = authorized_organization.timeseries()
    assert timeseries is not None
