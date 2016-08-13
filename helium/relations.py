"""Manage relationships between resources."""

from __future__ import unicode_literals
import inflection


class RelationType(object):
    INCLUDE = 0
    DIRECT = 1


def to_one(dest_class):
    def method_builder(cls):
        dest_resource_type = dest_class._resource_type()
        dest_method_name = dest_resource_type

        method_doc = """Fetch the {2} associated with this :class:`{0}`.

        Returns:

          {1}: The :class:`{1}` of this :class:`{0}`
        """.format(cls.__name__, dest_class.__name__, dest_method_name)

        def method(self):
            session = self.session
            id = None if hasattr(self, '_singleton') else self.id
            url = session._build_url(cls._resource_type(), id,
                                     dest_resource_type)
            json = dest_class._json(session.get(url), 200)
            return dest_class(json, session)

        method.__doc__ = method_doc
        setattr(cls, dest_method_name, method)
        return cls
    return method_builder


def to_many(dest_class, type=RelationType.DIRECT,
            reverse=None, reverse_type=RelationType.DIRECT,
            writable=False):
    def method_builder(cls):
        src_resource_type = cls._resource_type()
        dest_resource_type = dest_class._resource_type()
        dest_method_name = inflection.pluralize(dest_resource_type)
        doc_variables = {
            'from_class': cls.__name__,
            'to_class': dest_class.__name__,
            'to_name': dest_method_name
        }

        fetch_method_doc = """Fetch the {to_name} associated with this :class:`{from_class}`.

        Returns:

          iterable({to_class}): An iterator over all the :class:`{to_class}` of :class:`{from_class}`
        """

        def fetch_relationship_include(self):
            session = self.session
            id = None if hasattr(self, '_singleton') else self.id
            url = session._build_url(src_resource_type, id)
            params = {
                'include': dest_resource_type
            }
            json = dest_class._json(session.get(url, params=params), 200,
                                    extract="included")
            return [dest_class(entry, session) for entry in json]

        def fetch_relationship_direct(self):
            session = self.session
            id = None if hasattr(self, '_singleton') else self.id
            url = session._build_url(src_resource_type, id, dest_resource_type)
            json = dest_class._json(session.get(url), 200)
            return [dest_class(entry, session) for entry in json]

        if type == RelationType.DIRECT:
            fetch_relationship = fetch_relationship_direct
        elif type == RelationType.INCLUDE:
            fetch_relationship = fetch_relationship_include
        else:
            raise ValueError("Invalid RelationType: {}".format(type))
        fetch_relationship.__doc__ = fetch_method_doc

        def _update_relatonship(self, objs):
            session = self.session
            id = None if hasattr(self, '_singleton') else self.id
            url = session._build_url(src_resource_type, id,
                                     'relationships', dest_resource_type)
            ids = [obj.id for obj in objs]
            json = session._build_relationship(dest_resource_type, ids)
            dest_class._boolean(session.patch(url, json=json), 200)
            return objs

        def add_many(self, resources):
            """Add {to_name} to this :class:`{from_class}`.

            Args:

              resources: A list of :class:`{to_class}` to add
            """
            existing = fetch_relationship(self)
            target = set.union(set(existing), set(resources))
            return _update_relatonship(self, target)

        def remove_many(self, resources):
            """Remove {to_name} from this :class:`{from_class}`.

            Args:

              resources: A list of :class:`{to_class}` to remove
            """
            existing = fetch_relationship(self)
            target = set.difference(set(existing), set(resources))
            return _update_relatonship(self, target)

        def update_method(self, resources):
            """Set the {to_name} for this :class:`{from_class}`.

            To remove all {to_name} pass in an empty list.

            Args:

              resources: A list of :class:`{to_class}` to set
            """
            return _update_relatonship(self, resources)

        methods = [(dest_method_name, fetch_relationship)]
        if writable:
            methods.extend([
                ('add_{}'.format(dest_method_name), add_many),
                ('remove_{}'.format(dest_method_name), remove_many),
                ('update_{}'.format(dest_method_name), update_method)
            ])
        for name, method in methods:
            method.__doc__ = method.__doc__.format(**doc_variables)
            setattr(cls, name, method)

        if reverse is not None:
            reverse(cls, type=reverse_type)(dest_class)

        return cls

    return method_builder
