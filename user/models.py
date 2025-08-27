from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.core.exceptions import ValidationError
import os


USER_TYPE = [
    ('In', 'Sou uma pesquisador(a) ou inovador(a)'),
    ('Re', 'Não sou inovador(a), meu interesse é ler conteúdo'), 
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
    
# ----------------- ResearchArea (only for innovator verification) -----------------
class ResearchArea(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Área de Pesquisa"
        verbose_name_plural = "Áreas de Pesquisa"
        ordering = ["name"]

    def __str__(self):
        return self.name

class InnovatorVerification(models.Model):
    APPLICANT_CHOICES = [
        ("INDIVIDUAL", "Pessoa Física"),
        ("COMPANY", "Empresa/Instituição"),
    ]
    
    user = models.OneToOneField(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name="innovator_verification",
        )
    applicant_type = models.CharField(max_length=12, choices=APPLICANT_CHOICES)
    
    title = models.CharField(max_length=100)
    
    document = models.FileField(
        upload_to="verification_docs/",
        validators=[validate_doc_extension, validate_doc_size],
    )

    status = models.CharField(
        max_length=10,
        choices=[("PENDING", "Pendente"), ("APPROVED", "Aprovado"), ("REJECTED", "Rejeitado")],
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification({self.user.email}) - {self.status}"

    

