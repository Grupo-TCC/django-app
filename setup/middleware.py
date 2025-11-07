"""
InnovaSUS - Custom Middleware
"""
import time
import logging
from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


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
            
            # Log for debugging (remove in production)
            logger.debug(f"User {request.user.id} - Now: {now_ts}, Last: {last_activity}, Timeout: {self.timeout}")
            
            if last_activity:
                elapsed = now_ts - int(last_activity)
                logger.debug(f"User {request.user.id} - Elapsed: {elapsed}s, Max: {self.timeout}s")
                
                if elapsed > self.timeout:
                    logger.info(f"Logging out user {request.user.id} due to inactivity ({elapsed}s)")
                    
                    # Add a message before logout (if messages framework is available)
                    try:
                        messages.warning(
                            request, 
                            f'Sua sessão expirou devido à inatividade ({elapsed//60} minutos). Faça login novamente.'
                        )
                    except Exception as e:
                        logger.debug(f"Could not add message: {e}")
                    
                    logout(request)
                    # Continue with the request - user will be redirected to login if needed
            else:
                logger.debug(f"First request for user {request.user.id}, setting last_activity")
            
            # Update last activity timestamp on every authenticated request
            request.session['last_activity'] = now_ts
            request.session.save()  # Force save session
        
        response = self.get_response(request)
        return response