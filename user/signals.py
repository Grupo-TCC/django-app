from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import User
import os

# Delete old profile picture when updated
@receiver(pre_save, sender=User)
def auto_delete_old_profile_pic_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False  # skip if new user

    try:
        old_pic = User.objects.get(pk=instance.pk).profile_picture
    except User.DoesNotExist:
        return False

    new_pic = instance.profile_picture
    if old_pic and old_pic != new_pic:
        if os.path.isfile(old_pic.path):
            os.remove(old_pic.path)


# Delete profile picture from disk if user deleted
@receiver(post_delete, sender=User)
def auto_delete_profile_pic_on_delete(sender, instance, **kwargs):
    if instance.profile_picture:
        if os.path.isfile(instance.profile_picture.path):
            os.remove(instance.profile_picture.path)
