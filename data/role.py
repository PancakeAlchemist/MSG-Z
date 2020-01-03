from sqlalchemy import Column, Integer, String, BigInteger, Table, ForeignKey
from sqlalchemy.orm import relationship, backref

from data.base import Base


# users_roles_association = Table('Users_Roles', Base.metadata,
#     Column('UserId', BigInteger, ForeignKey('User.UserId')),
#     Column('RoleId', BigInteger, ForeignKey('Role.RoleId'))
# )

class Role(Base):
    __tablename__ = 'Roles'

    RoleId = Column(BigInteger, primary_key = True)
    Name = Column(String(32), nullable = False)

    #Users = relationship('User')

    def __init__(self, RoleId, Name):
        self.RoleId = RoleId
        self.Name = Name
        