from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import os




class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, fullname, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, fullname=fullname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user =  self.create_user(email, fullname, password, **extra_fields)
        
        return user 
    
class User(AbstractUser):
    username = None  # Remove username
    email = models.EmailField('email address', unique=True)

    fullname = models.CharField('full name', max_length=100)
    
    title = models.CharField(
        "title",
        max_length=100,
        blank=True,  # keep optional if you want
        null=True
    )
    
    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True,    
    )

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return settings.STATIC_URL + "assets/img/no_pic.jpg"
    
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    objects = UserManager()

    def __str__(self):
        return self.email
    
def validate_doc_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
        raise ValidationError("Formato inválido. Envie PDF, PNG, JPG ou JPEG.")
    
def validate_doc_size(value):
    limit_mb = 10
    if value.size > limit_mb * 1024 * 1024:
        raise ValidationError(f"Arquivo muito grande. Máx {limit_mb}MB.")
    

    
class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="following",
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="followers",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower.email} -> {self.following.email}"
    
    


    

