from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username is Required")
        if not email:
            raise ValueError("THe Email Field is Required")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=200, unique=True, null=False)
    email = models.EmailField(max_length=200, unique=True, null=False)
    password = models.CharField(max_length=200, null=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
class MovieUser(models.Model):
    mid = models.IntegerField(primary_key=True, unique=True, null=False)
    title = models.TextField()
    overview = models.TextField(blank=True, null=True)
    release_date = models.DateField()
    link = models.TextField()
    poster_path = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=10, decimal_places=2)
    genre = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.mid}"
    
class WatchList(models.Model):
    show_type = models.TextField(null=False, blank=False)
    u_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    m_id = models.ForeignKey(MovieUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.show_type