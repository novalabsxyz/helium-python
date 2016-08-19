"""Tests for Organization."""

from __future__ import unicode_literals
import pytest
import helium


def test_organization(authorized_organization):
    assert authorized_organization is not None


def test_update(authorized_organization):
    current_name = authorized_organization.name
    updated_org = authorized_organization.update(name="bar")
    assert updated_org.name == "bar"

    updated_org = authorized_organization.update(name=current_name)
    assert updated_org.name == current_name


def test_users(authorized_organization):
    users = authorized_organization.users()
    assert users is not None
    assert len(users) > 0

    # Reverse relationship, not quite deployed yet
    with pytest.raises(helium.NotFoundError):
        org = users[0].organization()
        assert org == authorized_organization


def test_metadata(authorized_organization):
    metadata = authorized_organization.metadata()
    assert metadata is not None


def test_timeseries(authorized_organization):
    timeseries = authorized_organization.timeseries()
    assert timeseries is not None


def test_meta(authorized_organization):
    assert authorized_organization.meta is not None
