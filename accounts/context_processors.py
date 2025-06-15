from .models import UserProfile

def user_profile(request):
    """Add user_profile to the template context for authenticated users"""
    context = {}
    if request.user.is_authenticated:
        try:
            context['user_profile'] = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass
    return context