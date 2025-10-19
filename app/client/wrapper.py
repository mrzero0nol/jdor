from functools import wraps
from app.service.auth import AuthInstance
import json

class SessionExpiredException(Exception):
    """Custom exception to signal a fatal session error."""
    pass

def handle_auth_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Initial attempt
        result = func(*args, **kwargs)

        is_auth_error = False
        if isinstance(result, dict):
            message = str(result.get("message", "")).lower()
            status = result.get("status", "")
            if status == "FAILED" and ("unauthorized" in message or "invalid token" in message or "invalid jwt" in message or "session not active" in message):
                is_auth_error = True

        if is_auth_error:
            print("\nSesi terdeteksi tidak valid, mencoba memperbarui secara otomatis...")
            if AuthInstance.renew_active_user_token():
                print("Sesi berhasil diperbarui. Mengulang permintaan...")
                new_tokens = AuthInstance.get_active_tokens()
                if not new_tokens:
                    print("\nGagal mendapatkan token baru setelah refresh. Sesi berakhir.")
                    AuthInstance.active_user = None
                    AuthInstance.write_active_number()
                    raise SessionExpiredException

                # Rebuild args for retry for send_api_request
                new_args = list(args)
                if func.__name__ == 'send_api_request' and len(new_args) >= 4:
                    new_args[3] = new_tokens['id_token'] # Update id_token
                    payload_dict = new_args[2]
                    if 'access_token' in payload_dict:
                        payload_dict['access_token'] = new_tokens['access_token']

                return func(*new_args, **kwargs)
            else:
                # Refresh failed, refresh token is invalid.
                print("\nGagal memperbarui sesi. Token refresh Anda sudah tidak berlaku.")
                print("Anda akan dikembalikan ke menu login.")
                AuthInstance.active_user = None
                AuthInstance.write_active_number() # remove active.number file
                raise SessionExpiredException

        return result
    return wrapper
