from django.conf import settings

class IPRestrictedBackend(ModelBackend):
    def authenticate(self, request: HttpRequest, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        
        if user:
            # Get the TradingAccount for the user and check the restrict_login flag
            trading_account = user.tradingaccount  # Assuming 1:1 relationship with TradingAccount
            
            # If restrict_login is enabled, check the IP
            if trading_account.restrict_login:
                allowed_ips = getattr(trading_account, 'allowed_ips', [])
                user_ip = request.META.get('REMOTE_ADDR', '')
                
                # If login from anywhere is not allowed, check the IP
                if user_ip not in allowed_ips and not settings.ALLOW_LOGIN_FROM_ANYWHERE:
                    return None
        return user
