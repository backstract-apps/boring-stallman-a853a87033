from pydantic import BaseModel,Field,field_validator

import datetime

import uuid

from typing import Any, Dict, List,Optional,Tuple,Union

import re

class Follows(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: Optional[str]=None


class ReadFollows(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: Optional[str]=None
    class Config:
        from_attributes = True


class Hashtags(BaseModel):
    id: int
    name: str
    usage_count: int
    created_at: Optional[str]=None


class ReadHashtags(BaseModel):
    id: int
    name: str
    usage_count: int
    created_at: Optional[str]=None
    class Config:
        from_attributes = True


class Likes(BaseModel):
    id: int
    user_id: int
    tweet_id: int
    created_at: Optional[str]=None


class ReadLikes(BaseModel):
    id: int
    user_id: int
    tweet_id: int
    created_at: Optional[str]=None
    class Config:
        from_attributes = True


class Replies(BaseModel):
    id: int
    user_id: int
    tweet_id: int
    content: str
    created_at: Optional[str]=None
    updated_at: Optional[str]=None


class ReadReplies(BaseModel):
    id: int
    user_id: int
    tweet_id: int
    content: str
    created_at: Optional[str]=None
    updated_at: Optional[str]=None
    class Config:
        from_attributes = True


class Retweets(BaseModel):
    id: int
    user_id: int
    tweet_id: int
    created_at: Optional[str]=None


class ReadRetweets(BaseModel):
    id: int
    user_id: int
    tweet_id: int
    created_at: Optional[str]=None
    class Config:
        from_attributes = True


class TweetHashtags(BaseModel):
    id: int
    tweet_id: int
    hashtag_id: int


class ReadTweetHashtags(BaseModel):
    id: int
    tweet_id: int
    hashtag_id: int
    class Config:
        from_attributes = True


class Tweets(BaseModel):
    id: int
    user_id: int
    content: str
    media_url: Optional[str]=None
    is_pinned: int
    created_at: Optional[str]=None
    updated_at: Optional[str]=None


class ReadTweets(BaseModel):
    id: int
    user_id: int
    content: str
    media_url: Optional[str]=None
    is_pinned: int
    created_at: Optional[str]=None
    updated_at: Optional[str]=None
    class Config:
        from_attributes = True


class UserProfiles(BaseModel):
    id: int
    user_id: int
    username: str
    display_name: str
    bio: Optional[str]=None
    avatar_url: Optional[str]=None
    is_private: int
    is_verified: int
    updated_at: Optional[str]=None


class ReadUserProfiles(BaseModel):
    id: int
    user_id: int
    username: str
    display_name: str
    bio: Optional[str]=None
    avatar_url: Optional[str]=None
    is_private: int
    is_verified: int
    updated_at: Optional[str]=None
    class Config:
        from_attributes = True


class Users(BaseModel):
    id: int
    email: str
    password: str
    created_at: Optional[str]=None


class ReadUsers(BaseModel):
    id: int
    email: str
    password: str
    created_at: Optional[str]=None
    class Config:
        from_attributes = True




class PostPlatformAuthPackageMaysonAuthUserLogin(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)

    class Config:
        from_attributes = True



class PostPlatformAuthPackageMaysonAuthUserRegister(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)

    class Config:
        from_attributes = True



# Query Parameter Validation Schemas

class GetLikesUserQueryParams(BaseModel):
    """Query parameter validation for get_likes_user"""
    user_id: int = Field(..., ge=1, description="User Id")
    limit: Optional[Union[int, float]] = Field(None)
    offset: Optional[Union[int, float]] = Field(None)

    class Config:
        populate_by_name = True


class GetRetweetsUserQueryParams(BaseModel):
    """Query parameter validation for get_retweets_user"""
    user_id: int = Field(..., ge=1, description="User Id")
    limit: Optional[Union[int, float]] = Field(None)
    offset: Optional[Union[int, float]] = Field(None)

    class Config:
        populate_by_name = True


class GetRepliesTweetQueryParams(BaseModel):
    """Query parameter validation for get_replies_tweet"""
    tweet_id: Optional[Union[int, float]] = Field(None)
    limit: Optional[Union[int, float]] = Field(None)
    offset: Optional[Union[int, float]] = Field(None)

    class Config:
        populate_by_name = True


class GetFollowsFollowersQueryParams(BaseModel):
    """Query parameter validation for get_follows_followers"""
    user_id: int = Field(..., ge=1, description="User Id")
    limit: Optional[Union[int, float]] = Field(None)
    offset: Optional[Union[int, float]] = Field(None)

    class Config:
        populate_by_name = True


class GetFollowsFollowingQueryParams(BaseModel):
    """Query parameter validation for get_follows_following"""
    user_id: int = Field(..., ge=1, description="User Id")
    limit: Optional[Union[int, float]] = Field(None)
    offset: Optional[Union[int, float]] = Field(None)

    class Config:
        populate_by_name = True
