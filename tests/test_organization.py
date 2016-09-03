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


def test_elements(authorized_organization):
    elements = authorized_organization.elements()
    assert elements is not None
    assert len(elements) > 0


def test_sensors(authorized_organization):
    sensors = authorized_organization.users()
    assert sensors is not None
    assert len(sensors) > 0


def test_labels(authorized_organization):
    labels = authorized_organization.users()
    assert labels is not None
    assert len(labels) > 0


def test_metadata(authorized_organization):
    metadata = authorized_organization.metadata()
    assert metadata is not None


def test_timeseries(authorized_organization):
    timeseries = authorized_organization.timeseries()
    assert timeseries is not None


def test_meta(authorized_organization):
    assert authorized_organization.meta is not None


def test_include(client, authorized_organization):
    include = [helium.Element, helium.User]
    org = helium.Organization.singleton(client, include=include)
    assert org is not None

    elements = org.elements(use_included=True)
    assert len(elements) > 0

    users = org.users(use_included=True)
    assert len(users) > 0

    with pytest.raises(AttributeError):
        authorized_organization.sensors(use_included=True)
