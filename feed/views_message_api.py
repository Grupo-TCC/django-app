from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Message
from user.models import User
from django.db import models
from django.http import HttpResponseBadRequest


@login_required
def send_message_api(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST only')
    user_id = request.POST.get('user_id')
    body = request.POST.get('body', '').strip()
    if not user_id or not body:
        return JsonResponse({'error': 'user_id and body required'}, status=400)
    try:
        other_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    msg = Message.objects.create(sender=request.user, recipient=other_user, body=body)
    return JsonResponse({'success': True, 'message': {
        'id': msg.id,
        'body': msg.body,
        'sender_id': msg.sender_id,
        'recipient_id': msg.recipient_id,
        'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
    }})

@login_required
def get_messages_api(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id required'}, status=400)
    try:
        other_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    messages = Message.objects.filter(
        (models.Q(sender=request.user, recipient=other_user) |
         models.Q(sender=other_user, recipient=request.user))
    ).order_by('created_at')
    data = [
        {
            'id': m.id,
            'body': m.body,
            'sender_id': m.sender_id,
            'recipient_id': m.recipient_id,
            'created_at': m.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        for m in messages
    ]
    return JsonResponse({'messages': data, 'user': {
        'id': other_user.id,
        'fullname': other_user.fullname,
        'profile_picture_url': other_user.get_profile_picture_url(),
    }})
