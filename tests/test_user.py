"""Test for Users."""

from __future__ import unicode_literals


def test_update(authorized_user):
    current_name = authorized_user.name
    updated_user = authorized_user.update(attributes={
        'name': 'bar'
    })
    assert updated_user.name == 'bar'
    assert updated_user == authorized_user

    updated_user = authorized_user.update(attributes={
        'name': current_name
    })
    assert updated_user.name == current_name


def test_meta(authorized_user):
    assert authorized_user.meta is not None
