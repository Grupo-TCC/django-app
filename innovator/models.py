from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# RESEARCH_CHOICES = [
#     ('TI', 'Tecnologia da Informação'),
#     ('EDU', 'Educação'),
#     ('ENG', 'Engenharia'),
#     ('CIE', 'CIÊNCIA'),
#     ('SAU', 'SAÚDE'),
#     ('TD', 'TODOS')
# ]

USER_TYPE = [
    ('Re', 'Reader'),
    ('In', 'Innovator') 
]

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
        
        extra_fields.setdefault('user_type', 'Re')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user =  self.create_user(email, fullname, password, **extra_fields)
        # default_area, _ = ResearchArea.objects.get_or_create(code='TD', name='TODOS')
        # user.research_areas.add(default_area)
        return user

# class ResearchArea(models.Model):
#     code = models.CharField(max_length=100, unique=True)
#     name = models.CharField(max_length=100)
    
#     def __str__(self):
#         return self.name
    
    
class User(AbstractUser):
    username = None  # Remove username
    email = models.EmailField('email address', unique=True)

    fullname = models.CharField('full name', max_length=100)
    # research_areas = models.ManyToManyField(
    #     'ResearchArea', blank=True
    # )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE,
        default='Re'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    objects = UserManager()

    def __str__(self):
        return self.email
