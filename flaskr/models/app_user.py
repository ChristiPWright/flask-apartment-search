from flaskr import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class AppUser(db.Model):
    __tablename__ = 'app_users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(256), nullable=True)
    profile_picture = db.Column(db.String(256), nullable=True)
    email = db.Column(db.String(256), nullable=False, unique=True)