# from app.core.security import (
#     create_access_token,
#     verify_password,
#     get_password_hash,
#     create_access_refresh_tokens,
#     create_tokens_with_refresh_token,
#     create_jwt_token,
#     create_refresh_token,
#     ALGORITHM,
# )
# from datetime import timedelta
# from app.core.dependencies import get_current_user, get_asana_client_in_password_flow


# def test_security_and_depends():

#     ### Test Security Functions ###

#     password = "password"
#     hashed_password = get_password_hash(password)
#     assert verify_password(password, hashed_password), "failed"

#     ### Test JWT Token Functions ###
#     user_id = "user_id"

#     access_token = create_access_token(user_id=user_id)
#     assert access_token, "failed"

#     refresh_token = create_refresh_token(user_id=user_id)
#     assert refresh_token, "failed"

#     access_refresh_tokens = create_access_refresh_tokens(user_id=user_id)
#     assert access_refresh_tokens, "failed"

#     ### Test JWT Token Decode ###

#     ### Test other functions ###

#     expires_delta = timedelta(minutes=1)
#     scope = "scope"
#     encoded_jwt = create_jwt_token(expires_delta, scope, user_id)
#     assert encoded_jwt, "failed"

#     tokens = create_tokens_with_refresh_token(refresh_token)
#     assert tokens, "failed"

#     ### Test Depends Functions ###

#     user = get_current_user(token=access_token)
#     assert user, "failed"

#     asana_client = get_asana_client_in_password_flow(user=user)
#     assert asana_client, "failed"
