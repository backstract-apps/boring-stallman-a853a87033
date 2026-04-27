from sqlalchemy.orm import Session, aliased
from database import SessionLocal
from sqlalchemy import and_, or_
from typing import *
from loguru import logger
from fastapi import Request, UploadFile, HTTPException, status
from fastapi.responses import RedirectResponse, StreamingResponse
import models, schemas
import boto3
import jwt
from datetime import datetime
import requests
import math
import os
import json
import random
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    RunConfig,
    ModelSettings,
    InputGuardrail,
    OutputGuardrail,
)
import agent_session_store as store


load_dotenv()


def convert_to_datetime(date_string):
    if date_string is None:
        return datetime.now()
    if not date_string.strip():
        return datetime.now()
    if "T" in date_string:
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except ValueError:
            date_part = date_string.split("T")[0]
            try:
                return datetime.strptime(date_part, "%Y-%m-%d")
            except ValueError:
                return datetime.now()
    else:
        # Try to determine format based on first segment
        parts = date_string.split("-")
        if len(parts[0]) == 4:
            # Likely YYYY-MM-DD format
            try:
                return datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return datetime.now()

        # Try DD-MM-YYYY format
        try:
            return datetime.strptime(date_string, "%d-%m-%Y")
        except ValueError:
            return datetime.now()

        # Fallback: try YYYY-MM-DD if not already tried
        if len(parts[0]) != 4:
            try:
                return datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return datetime.now()

        return datetime.now()


class SessionStoreAdapter:

    def load_session(self, session_id: str) -> dict:
        return store.load_session_memory(session_id)

    def save_session(self, session_id: str, data: dict) -> None:
        store.save_session_memory(session_id, data)


_memory_adapter = SessionStoreAdapter()


async def agent_create_session(body: str):
    """Start a new chat session."""
    meta = store.create_session(title=body, session_id=body)
    return meta


async def agent_get_history(session_id: str):
    """Return the human-readable message history for a session."""
    if not store.get_session(session_id):
        raise HTTPException(404, "Session not found")
    messages = store.get_chat_history(session_id)
    return {"session_id": session_id, "messages": messages}


async def _agent_generate_title(
    first_message: str, run_config: RunConfig, agent: Agent
) -> str:
    """Ask the LLM for a short 4-word session title from the first user message."""
    try:
        result = await asyncio.wait_for(
            Runner.run(
                agent,
                f"Give a 4-word title (no quotes, no punctuation) that summarises this message: {first_message[:300]}",
                run_config=run_config,
            ),
            timeout=15,
        )
        title = str(result.final_output).strip()[:60]
        return title if title else first_message[:40]
    except Exception:
        return first_message[:40]


async def get_platform_auth_package_mayson_sso_auth_callback(
    request: Request, db: Session
):

    user_identity: str = "i"

    user_password: str = "top_secret_area_51"

    from passlib.hash import md5_crypt

    encrypt_pass = md5_crypt.hash(user_password)

    # get user email from request

    try:
        param_obj = dict(request.query_params)

        not_found_page = "https://mayson.dev/not-found"
        user_identity = param_obj.get(
            "user_email", "no-user-identity-received-from-backend"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == user_identity))
    has_a_record = query.count() > 0

    if has_a_record:
        pass

    else:

        record_to_be_added = {"email": user_identity, "password": encrypt_pass}
        new_users = models.Users(**record_to_be_added)
        db.add(new_users)
        db.commit()
        db.refresh(new_users)
        post_user_record = new_users.to_dict()

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == user_identity))

    user_record = query.first()

    user_record = (
        (
            user_record.to_dict()
            if hasattr(user_record, "to_dict")
            else vars(user_record)
        )
        if user_record
        else user_record
    )

    import jwt
    from datetime import timezone

    secret_key = """aJ62hJhbAYL6_SoWTjSI-lTbC1m0qErEgEwVK3IGwBfql3mChNSVzjJAzW337Gp9"""
    bs_jwt_payload = {
        "exp": int(datetime.now(timezone.utc).timestamp() + 86400),
        "data": user_record,
    }

    generated_jwt = jwt.encode(bs_jwt_payload, secret_key, algorithm="HS256")

    # define client

    try:
        request_token = generated_jwt or "no-generated-jwt"
        request_provider = param_obj.get("provider", "no-provider-from-backend")
        final_url = f'{param_obj.get("frontend-redirect", not_found_page)}?token={request_token}&provider={request_provider}'

        return RedirectResponse(url=final_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"message": "success_response"},
    }
    return res


async def post_platform_auth_package_mayson_auth_user_login(
    request: Request,
    db: Session,
    raw_data: schemas.PostPlatformAuthPackageMaysonAuthUserLogin,
):
    email: str = raw_data.email
    password: str = raw_data.password

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == email))

    oneRecord = query.first()

    oneRecord = (
        (oneRecord.to_dict() if hasattr(oneRecord, "to_dict") else vars(oneRecord))
        if oneRecord
        else oneRecord
    )

    if oneRecord:
        from passlib.hash import md5_crypt

        password_hash_mayson = oneRecord["password"]
        password_valid = md5_crypt.verify(password, password_hash_mayson)
        if password_valid:
            validated_password = True
        else:
            validated_password = False
    else:
        validated_password = False

    login_status: str = "Login initiated"

    if validated_password:

        login_status = "Login success"

    else:

        raise HTTPException(status_code=401, detail="Bad credentials.")

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == email))

    user_record = query.first()

    user_record = (
        (
            user_record.to_dict()
            if hasattr(user_record, "to_dict")
            else vars(user_record)
        )
        if user_record
        else user_record
    )

    import jwt
    from datetime import timezone

    secret_key = """aJ62hJhbAYL6_SoWTjSI-lTbC1m0qErEgEwVK3IGwBfql3mChNSVzjJAzW337Gp9"""
    bs_jwt_payload = {
        "exp": int(datetime.now(timezone.utc).timestamp() + 86400),
        "data": user_record,
    }

    generated_jwt = jwt.encode(bs_jwt_payload, secret_key, algorithm="HS256")

    login_status = "Login successful"

    res = {
        "status": 200,
        "message": "Login successful",
        "data": {"jwt": generated_jwt, "login_status": login_status},
    }
    return res


async def post_tweets(request: Request, db: Session):
    res = {}
    return res


async def put_tweets_id(request: Request, db: Session):
    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {},
    }
    return res


async def post_retweets(request: Request, db: Session):
    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {},
    }
    return res


async def get_platform_auth_package_mayson_sso_auth_me(request: Request, db: Session):

    # get auth header

    try:
        auth_header = request.headers.get("authorization")
        auth_header = (
            auth_header[7:]
            if auth_header and auth_header.lower().startswith("bearer ")
            else auth_header
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    import jwt

    try:
        user_profile = jwt.decode(
            auth_header,
            """aJ62hJhbAYL6_SoWTjSI-lTbC1m0qErEgEwVK3IGwBfql3mChNSVzjJAzW337Gp9""",
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

    # profile_data = user_profile["data"]

    try:
        profile_data = user_profile["data"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"user_profile": profile_data},
    }
    return res


async def post_platform_auth_package_mayson_auth_user_register(
    request: Request,
    db: Session,
    raw_data: schemas.PostPlatformAuthPackageMaysonAuthUserRegister,
):
    email: str = raw_data.email
    password: str = raw_data.password

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == email))

    existing_record = query.first()

    existing_record = (
        (
            existing_record.to_dict()
            if hasattr(existing_record, "to_dict")
            else vars(existing_record)
        )
        if existing_record
        else existing_record
    )

    if existing_record:

        raise HTTPException(status_code=400, detail="User already exists.")
    else:
        pass

    from passlib.hash import md5_crypt

    encrypt_pass = md5_crypt.hash(password)

    record_to_be_added = {"email": email, "password": encrypt_pass}
    new_users = models.Users(**record_to_be_added)
    db.add(new_users)
    db.commit()
    db.refresh(new_users)
    post_user_record = new_users.to_dict()

    res = {"status": 200, "message": "User registered successfully", "data": {}}
    return res


async def post_tweet_hashtags(request: Request, db: Session):
    res = {}
    return res


async def post_follows(request: Request, db: Session):
    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {},
    }
    return res


async def get_platform_auth_package_mayson_sso_auth_login_google(
    request: Request, db: Session
):

    # define client

    try:
        import httpx

        async def google_login():
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": "Bearer v4.public.eyJlbWFpbF9pZCI6ICJzaGl2YW0uc3JpdmFzdGF2YUBub3Zvc3RhY2suY29tIiwgInVzZXJfaWQiOiAiNzk0ZjFlMzZjNmMzNDRjMzk3ODIwN2ZmMjRkOGFkNzgiLCAib3JnX2lkIjogIk5BIiwgInN0YXRlIjogInNpZ251cCIsICJyb2xlX25hbWUiOiAiTkEiLCAicm9sZV9pZCI6ICJOQSIsICJwbGFuX2lkIjogIjEwMSIsICJhY2NvdW50X3ZlcmlmaWVkIjogIjEiLCAiYWNjb3VudF9zdGF0dXMiOiAiMCIsICJ1c2VyX25hbWUiOiAiNzk0ZjFlMzZjNmMzNDRjMzk3ODIwN2ZmMjRkOGFkNzgiLCAic2lnbnVwX3F1ZXN0aW9uIjogMCwgInRva2VuX2xpbWl0IjogbnVsbCwgInRva2VuX3R5cGUiOiAiYWNjZXNzIiwgImV4cCI6IDE3Nzc4OTcxNDgsICJleHBpcnlfdGltZSI6IDE3Nzc4OTcxNDh9tseFl4BEOS7CvRBxQTy6Ey_fNQHb3RLceoGHXTttvn6aMnFZNChEs-UG_pkzDEPLFrmQCK3ONhNtVXmuEMppCg",
                    "Content-Type": "application/json",
                }

                res = await client.get(
                    "https://api-release.beemerbenzbentley.site/sigma/api/v1/sso/auth/google/login?collection_id=coll_c766e74b4a974272b188e43d174331e7",
                    headers=headers,
                )

            res.raise_for_status()

            try:
                response_obj = dict(res.json())
                final_url = response_obj.get("value")
                return final_url
            except Exception as e:
                return f"https://mayson.dev/not-found?reason={str(e)}"

        return RedirectResponse(url=await google_login())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"message": "success_response"},
    }
    return res


async def delete_tweets_id(request: Request, db: Session):
    res = {}
    return res


async def delete_retweets_id(request: Request, db: Session):
    res = {}
    return res


async def delete_replies_id(request: Request, db: Session):
    res = {}
    return res


async def get_tweets(request: Request, db: Session):
    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {},
    }
    return res


async def delete_likes_id(request: Request, db: Session):
    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {},
    }
    return res


async def get_tweets_id(request: Request, db: Session):
    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {},
    }
    return res


async def delete_follows_id(request: Request, db: Session):
    res = {}
    return res


async def get_hashtags(request: Request, db: Session):
    res = {}
    return res


async def post_replies(request: Request, db: Session):
    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {},
    }
    return res


async def post_likes(request: Request, db: Session):
    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {},
    }
    return res


async def get_likes_user(
    request: Request,
    db: Session,
    user_id: Union[int, float],
    limit: Union[int, float],
    offset: Union[int, float],
):

    tweets = aliased(models.Tweets)
    query = db.query(models.Likes, tweets)

    query = query.join(tweets, and_(models.Likes.id == likes["tweet_id"]))
    query = query.filter(and_(models.Likes.user_id == user_id))

    query = query.order_by(models.Likes.created_at.desc())

    query = query.limit(limit)

    liked_tweets = query.all()
    liked_tweets = (
        [
            {
                "liked_tweets_1": (
                    s1.to_dict() if hasattr(s1, "to_dict") else s1.__dict__
                ),
                "liked_tweets_2": (
                    s2.to_dict() if hasattr(s2, "to_dict") else s2.__dict__
                ),
            }
            for s1, s2 in liked_tweets
        ]
        if liked_tweets
        else liked_tweets
    )

    # Return 404 if no likes are found for the user
    raise HTTPException(status_code=404, detail="No likes found for this user")

    res = {
        "status": 200,
        "message": "User likes retrieved successfully",
        "data": {"likes": "likes_list", "total": "total_count"},
    }
    return res


async def get_retweets_user(
    request: Request,
    db: Session,
    user_id: Union[int, float],
    limit: Union[int, float],
    offset: Union[int, float],
):

    tweets = aliased(models.Tweets)
    query = db.query(models.Retweets, tweets)

    query = query.join(tweets, and_(models.Retweets.id == retweets["tweet_id"]))
    query = query.filter(and_(models.Retweets.user_id == user_id))

    query = query.order_by(models.Retweets.retweets.created_at.desc())

    query = query.limit(limit)

    retweets_list = query.all()
    retweets_list = (
        [
            {
                "retweets_list_1": (
                    s1.to_dict() if hasattr(s1, "to_dict") else s1.__dict__
                ),
                "retweets_list_2": (
                    s2.to_dict() if hasattr(s2, "to_dict") else s2.__dict__
                ),
            }
            for s1, s2 in retweets_list
        ]
        if retweets_list
        else retweets_list
    )

    res = {
        "status": 200,
        "message": "User retweets retrieved successfully",
        "data": {"total": "total_count", "retweets": retweets_list},
    }
    return res


async def get_replies_tweet(
    request: Request,
    db: Session,
    tweet_id: Union[int, float],
    limit: Union[int, float],
    offset: Union[int, float],
):

    query = db.query(models.Replies)
    query = query.filter(and_(models.Replies.tweet_id == tweet_id))

    query = query.order_by(models.Replies.created_at.desc())

    query = query.limit(limit)

    replies_list = query.all()
    replies_list = (
        [new_data.to_dict() for new_data in replies_list]
        if replies_list
        else replies_list
    )

    res = {
        "status": 200,
        "message": "Replies retrieved successfully",
        "data": {"total": "total_count", "replies": replies_list},
    }
    return res


async def get_follows_followers(
    request: Request,
    db: Session,
    user_id: Union[int, float],
    limit: Union[int, float],
    offset: Union[int, float],
):

    users = aliased(models.Users)
    query = db.query(models.Follows, users)

    query = query.join(users, and_(models.Follows.id == follows["follower_id"]))
    query = query.filter(and_(models.Follows.following_id == user_id))

    query = query.order_by(models.Follows.created_at.desc())

    query = query.limit(limit)

    followers = query.all()
    followers = (
        [
            {
                "followers_1": s1.to_dict() if hasattr(s1, "to_dict") else s1.__dict__,
                "followers_2": s2.to_dict() if hasattr(s2, "to_dict") else s2.__dict__,
            }
            for s1, s2 in followers
        ]
        if followers
        else followers
    )

    res = {
        "status": 200,
        "message": "Followers retrieved successfully",
        "data": {"total": "total_count", "followers": "followers_list"},
    }
    return res


async def get_follows_following(
    request: Request,
    db: Session,
    user_id: Union[int, float],
    limit: Union[int, float],
    offset: Union[int, float],
):

    users = aliased(models.Users)
    query = db.query(models.Follows, users)

    query = query.join(users, and_(models.Follows.id == follows["following_id"]))
    query = query.filter(and_(models.Follows.follower_id == user_id))

    query = query.order_by(models.Follows.created_at.desc())

    query = query.limit(limit)

    follows_with_users = query.all()
    follows_with_users = (
        [
            {
                "follows_with_users_1": (
                    s1.to_dict() if hasattr(s1, "to_dict") else s1.__dict__
                ),
                "follows_with_users_2": (
                    s2.to_dict() if hasattr(s2, "to_dict") else s2.__dict__
                ),
            }
            for s1, s2 in follows_with_users
        ]
        if follows_with_users
        else follows_with_users
    )

    query = db.query(models.Follows)
    query = query.filter(and_(models.Follows.follower_id == user_id))

    follows_total = query.all()
    follows_total = (
        [new_data.to_dict() for new_data in follows_total]
        if follows_total
        else follows_total
    )

    res = {
        "status": 200,
        "message": "Following retrieved successfully",
        "data": {"total": "total_count", "following": "following_list"},
    }
    return res
