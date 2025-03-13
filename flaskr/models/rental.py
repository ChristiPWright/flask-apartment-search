from flaskr import db
import uuid
import sqlalchemy
from sqlalchemy.dialects.postgresql import UUID, MONEY

class Rental(db.Model):
    __tablename__ = 'rentals'

    rental_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    lister_id = db.Column(UUID(as_uuid=True), db.ForeignKey('app_users.user_id', ondelete='CASCADE'), nullable=False)      
    title = db.Column(db.String(256), nullable=True)
    description = db.Column(db.String(256), nullable=True)
    address = db.Column(db.String(256), nullable=False)
    price = db.Column(MONEY, nullable=False)
    status = db.Column(sqlalchemy.Enum('active', 'inactive', name='rental_status', create_type=True), nullable=False, default='active')
