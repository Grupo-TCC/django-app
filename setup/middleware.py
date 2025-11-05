"""
InnovaSUS - Custom Middleware
"""
import time
from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect


class InactivityLogoutMiddleware:
    """
    Logs out authenticated users after a period of inactivity.
    Configure timeout in settings: INACTIVITY_TIMEOUT_SECONDS (default 1800 = 30m).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Default to 30 minutes if not set
        self.timeout = getattr(settings, 'INACTIVITY_TIMEOUT_SECONDS', 1800)
    
    def __call__(self, request):
        if request.user.is_authenticated:
            now_ts = int(time.time())
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                elapsed = now_ts - int(last_activity)
                if elapsed > self.timeout:
                    # Add a message before logout (if messages framework is available)
                    try:
                        messages.warning(
                            request, 
                            'Sua sessão expirou devido à inatividade. Faça login novamente.'
                        )
                    except Exception:
                        # If messages framework is not available, continue without message
                        pass
                    logout(request)
                    # Continue with the request - user will be redirected to login if needed
            
            # Update last activity timestamp on every authenticated request
            request.session['last_activity'] = now_ts
        
        response = self.get_response(request)
        return response