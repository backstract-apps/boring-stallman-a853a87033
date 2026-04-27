from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import class_mapper
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, Float, Text, ForeignKey, JSON, Numeric, Date, \
    TIMESTAMP, UUID, LargeBinary, text as text_sql, Interval
from sqlalchemy.types import Enum
from sqlalchemy.ext.declarative import declarative_base


@as_declarative()
class Base:
    id: int
    __name__: str

    # Auto-generate table name if not provided
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # Generic to_dict() method
    def to_dict(self):
        """
        Converts the SQLAlchemy model instance to a dictionary, ensuring UUID fields are converted to strings.
        """
        result = {}
        for column in class_mapper(self.__class__).columns:
            value = getattr(self, column.key)
                # Handle UUID fields
            if isinstance(value, uuid.UUID):
                value = str(value)
            # Handle datetime fields
            elif isinstance(value, datetime):
                value = value.isoformat()  # Convert to ISO 8601 string
            # Handle Decimal fields
            elif isinstance(value, Decimal):
                value = float(value)

            result[column.key] = value
        return result




class Follows(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer)
    following_id = Column(Integer)
    created_at = Column(String, nullable=True)


class Hashtags(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    usage_count = Column(Integer)
    created_at = Column(String, nullable=True)


class Likes(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    tweet_id = Column(Integer)
    created_at = Column(String, nullable=True)


class Replies(Base):
    __tablename__ = "replies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    tweet_id = Column(Integer)
    content = Column(String)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)


class Retweets(Base):
    __tablename__ = "retweets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    tweet_id = Column(Integer)
    created_at = Column(String, nullable=True)


class TweetHashtags(Base):
    __tablename__ = "tweet_hashtags"

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer)
    hashtag_id = Column(Integer)


class Tweets(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    content = Column(String)
    media_url = Column(String, nullable=True)
    is_pinned = Column(Integer)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)


class UserProfiles(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    display_name = Column(String)
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_private = Column(Integer)
    is_verified = Column(Integer)
    updated_at = Column(String, nullable=True)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    created_at = Column(String, nullable=True)


