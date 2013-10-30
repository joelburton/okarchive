import hashlib

from sqlalchemy import (
    Column,
    String,
)

from . import Base


class User(Base):
    """System user."""

    __tablename__ = 'users'

    name = Column(
        String,
        primary_key=True,
    )
    password_md5 = Column(
        String,
        nullable=False,
    )

    def verifyPassword(self, password):
        """Verify password."""

        md5 = hashlib.md5(password.encode()).hexdigest()
        return md5 == self.password_md5

