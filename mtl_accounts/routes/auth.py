import os

from fastapi import APIRouter, Depends, Request
from fastapi_jwt_auth import AuthJWT
from mtl_accounts.database.conn import db
from mtl_accounts.database.crud import create_users
from mtl_accounts.database.schema import Users
from mtl_accounts.models import UserToken
from mtl_accounts.util.microsoft import MicrosoftCustomSSO
from sqlalchemy.orm import Session

router = APIRouter()

microsoft_sso = MicrosoftCustomSSO(
    client_id=os.getenv("MY_CLIENT_ID"),
    client_secret=os.getenv("MY_CLIENT_SECRET"),
    client_tenant=os.getenv("MY_CLIENT_TENANT"),
    redirect_uri=os.getenv("REDIRECT_URL"),
    allow_insecure_http=True,
    use_state=False,
)


@router.get("/test")
async def authorize_test(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_raw_jwt()
    return {"test": current_user}


@router.get("/microsoft/login")
async def microsoft_login():
    return await microsoft_sso.get_login_redirect()


@router.get("/microsoft/callback")
async def microsoft_callback(request: Request, Authorize: AuthJWT = Depends(), session: Session = Depends(db.session)):
    user = await microsoft_sso.verify_and_process(request)

    account = session.query(Users).filter(Users.mail == user["mail"]).first()

    user = UserToken(**user, provider="office365", role="default")
    if account is None:
        create_users(session, user)
    else:
        user.role = account.role

    access_token = Authorize.create_access_token(subject=user.mail, user_claims=user.dict())
    refresh_token = Authorize.create_refresh_token(subject=user.mail, user_claims=user.dict())
    Authorize.set_refresh_cookies(refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh")
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    current_user = Authorize.get_raw_jwt()
    current_user["type"] = "access"
    new_access_token = Authorize.create_access_token(subject=current_user["sub"], user_claims=current_user)
    return {"new_access_token": new_access_token}


@router.delete("/delete")
def delete(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    Authorize.unset_jwt_cookies()
    return {"msg": "Successfully logout"}
