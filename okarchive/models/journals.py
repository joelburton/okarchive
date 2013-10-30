from . import DBSession, siteRoot
from .journal import Journal


class Journals:
    """Traversable container for journals."""

    __name__ = 'journals'
    __parent__ = siteRoot

    def __getitem__(self, item):
        """Get journal by name."""

        journal = (DBSession
                   .query(Journal)
                   .filter_by(name=item)
                   .first())
        if not journal:
            raise KeyError('No such journal: {}'.format(item))
        return journal

    def __setitem__(self, key, value):
        """Add a journal."""

        raise NotImplementedError("Can't add journal")

    def __delitem__(self, key):
        """Delete a journal."""

        raise NotImplementedError("Can't delete journal")

    def values(self):
        """List of journals."""

        return [j for j in self.journals]

    def keys(self):
        """List of journal names."""

        return [j.name for j in self.journals]

    def items(self):
        """List of (journal-name, journal) tuples."""

        return [(j.name, j) for j in self.journals]

    @property
    def journals(self):
        """Return list of journals."""

        # XXX: do we need to worry about getting journals without a sort order?
        return (DBSession
                .query(Journal)
                .order_by(Journal.name)
        )


journals = Journals()
