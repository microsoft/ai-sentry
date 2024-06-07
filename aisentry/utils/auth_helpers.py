from flask import Flask

# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

class OriginalHttpRequest:
    def __init__(self, request_headers, params, response_body):
        self.request_headers = request_headers
        self.params = params
        self.response_body = response_body

    


# @app.errorhandler(AuthError)
# def handle_auth_error(ex):
#     print('handling error')
#     response = jsonify(ex.error)
#     response.status_code = ex.status_code
#     return response

# def get_token_auth_header():
#     """Obtains the Access Token from the Authorization Header
#     """
#     auth = request.headers.get("Authorization", None)
#     if not auth:
#         raise AuthError({"code": "authorization_header_missing",
#                         "description":
#                         "Authorization header is expected"}, 401)

#     parts = auth.split()

#     if parts[0].lower() != "bearer":
#         raise AuthError({"code": "invalid_header",
#                         "description":
#                         "Authorization header must start with"
#                         " Bearer"}, 401)
#     elif len(parts) == 1:
#         raise AuthError({"code": "invalid_header",
#                         "description": "Token not found"}, 401)
#     elif len(parts) > 2:
#         raise AuthError({"code": "invalid_header",
#                         "description":
#                         "Authorization header must be"
#                         " Bearer token"}, 401)

#     token = parts[1]
#     return token




# def verify_jwt(tenant_id: str, audience: str = None):
#     try:

#         bearer_token = get_token_auth_header()
#         #unverified_header = jwt.get_unverified_header(bearer_token)

#         signing_key = jwks_client.get_signing_key_from_jwt(bearer_token)


#         data = jwt.api_jwt.decode_complete(
#                     bearer_token,
#                     signing_key.key,
#                     algorithms=["RS256"],
#                     audience=AUDIENCE,
#                     issuer="https://sts.windows.net/" + tenant_id + "/"
#                 )
        
#         payload, header = data["payload"], data["header"]

#         print(f"payload: {payload}")
#         print(f"header: {header}")
#         #alg_obj = jwt.get_algorithm_by_name(header["alg"])
#         return True
#     except Exception as e:
#         raise AuthError({"code": "invalid_header",
#                                 "description":
#                                 "Unable to verify authentication"
#                                 f" token with error {e}"}, 401)

   
#     raise AuthError({"code": "invalid_header",
#                          "description": "Unable to find appropriate key"}, 401)
    
#         #jwt_keys[tenant_id] = jwks
    


# @app.route('/helloauth', methods=['POST'])
# async def hello_auth() -> Tuple[dict, str]:
#     bearer_token = get_token_auth_header()
#     verify_jwt("d3edbe6c-8eda-4e97-8370-86961098c24c")
#     jwt_token = jwt.get_unverified_header(bearer_token)

#     return jsonify(message=f"Hello, World {name}! and token {jwt_token}")