# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""
from .extensions import db

# Alias common SQLAlchemy names
Column = db.Column
relationship = db.relationship


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True


class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class.

    From Mike Bayer's "Building the app" talk
    https://speakerdeck.com/zzzeek/building-the-app
    """

    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get a record by its ID."""
        if any((isinstance(record_id, (str, bytes)) and record_id.isdigit(), isinstance(record_id, (int, float))),):
            return cls.query.get(int(record_id))
        return None


def reference_column(table_name, nullable=False, pk_name="id", **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_column('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(db.ForeignKey("{}.{}".format(table_name, pk_name)), nullable=nullable, **kwargs)
