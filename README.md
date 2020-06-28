
## Create Custom User Model

- First create an app named `core` then specify `User` model

`core.models`
```python
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,\
    PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """Creates and saves a new user"""
        if not email:
            raise ValueError("No email provided")
        # normalize_email is built in to lower chars
        user = self.model(email=self.normalize_email(email), **kwargs)
        # Use built in django helper function to store password
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
```

`core.tests.test_models`
```python
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@ekocibar.com'
        password = 'Testpassword123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_email_field(self):
        """Test whether email is normalized on user creation"""
        email = 'test@EKOCIBAR.COM'
        password = 'Testpassword123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test whether email is valid on user creation"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@ekocibar.com',
            'test1234'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
```

### Commands used

```sh
docker-compose run app sh -c "django-admin.py startapp core"
docker-compose run app sh -c "python manage.py makemigrations"
docker build .
docker-compose build
docker-compose run app sh -c "python manage.py test && flake8"
```


### Do not forget to!

- add `core` app to `INSTALLED_APPS`
- add `AUTH_USER_MODEL = 'core.User'` to specify user
