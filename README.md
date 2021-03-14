
## Create user management endpoints
- Create user app,
- Create token for authentication,

#### Create user app
   - `docker-compose run --rm app sh -c "python manage.py startapp user"`
   - Remove `migrations`, `models`, because we keep all in the  `core` app
   - Add `rest_framework` and `user` app to INSTALLED_APPS in `settings.py`
       ```
          'rest_framework',
          'rest_framework.authtoken',
          'user',```
   - Add tests for creating users
   - Add serializers, views for creating users
   - Manage urls

`app/user/tests/test_user_api.py`
```diff
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """ Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@ekocibar.nl',
            'password': 'testpass',
            'name': 'Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exists fails"""
        payload = {'email': 'test@ekocibar.nl', 'password': 'testpass'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the passwprd must be more than 5 characters"""
        payload = {
            'email': 'test@ekocibar.nl',
            'password': 'shor',
            'name': 'Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
```


`app/user/serializers.py`
```diff
from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

```


`app/user/views.py`
```diff
from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer

```


`app/user/urls.py`
```diff
from django.urls import path

from . import views


app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create')
]
```

`app/user/urls.py`
```diff
from django.contrib import admin
-from django.urls import path
+from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
+   path('api/user/', include('user.urls')),
]
```

#### Create token for authentication
   - Add a serializer to validate and create token for users
   - Create `token/` endpoint

`app/user/tests/test_user_api.py`
```diff
    .
    .
+   TOKEN_URL = reverse('user:token')
    .
    .


+   def test_create_token_for_user(self):
+       """Test that a yoken is created for the user"""
+       payload = {'email': 'test@ekocibar.nl', 'password': 'testpass'}
+       create_user(**payload)
+       res = self.client.post(TOKEN_URL, payload)
+
+       self.assertIn('token', res.data)
+       self.assertEqual(res.status_code, status.HTTP_200_OK)
+
+   def test_create_toke_invalid_credentials(self):
+       """Test that token is not created if invalid credentials are given"""
+       create_user(email='test@ekocibar.nl', password='testpass')
+       payload = {'email': 'test@ekocibar.nl', 'password': 'wrongpassword'}
+       res = self.client.post(TOKEN_URL, payload)
+
+       self.assertNotIn('token', res.data)
+       self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
+
+   def test_create_token_no_user(self):
+       """Test that token is not created if user doesn't exist"""
+       payload = {'email': 'test@ekocibar.nl', 'password': 'testpass'}
+       res = self.client.post(TOKEN_URL, payload)
+
+       self.assertNotIn('token', res.data)
+       self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
+
+   def test_create_token_missing_field(self):
+       """Test that email and password are required"""
+       res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
+
+       self.assertNotIn('token', res.data)
+       self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
```

`app/user/serializers.py`
```diff
-from django.contrib.auth import get_user_model
+from django.contrib.auth import get_user_model, authenticate
+from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


+class AuthTokenSerializer(serializers.Serializer):
+   """Serializer for the user authentication object"""
+   email = serializers.CharField()
+   password = serializers.CharField(
+       style={'input_type': 'password'},
+       trim_whitespace=False
+   )
+
+   def validate(self, attrs):
+       """Validate and authenticate the user"""
+       email = attrs.get('email')
+       password = attrs.get('password')
+
+       user = authenticate(
+           request=self.context.get('request'),
+           username=email,
+           password=password
+       )
+       if not user:
+           msg = _('Unable to authenticate with provided credentials')
+           raise serializers.ValidationError(msg, code='authentication')
+
+       attrs['user'] = user
+       return attrs

```

`app/user/views.py`
```diff
from rest_framework import generics
+from rest_framework.authtoken.views import ObtainAuthToken
+from rest_framework.settings import api_settings

-from user.serializers import UserSerializer
+from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


+class CreateTokenView(ObtainAuthToken):
+   """Create a new auth token for user"""
+   serializer_class = AuthTokenSerializer
+   renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
```

`app/user/urls.py`
```diff
from django.urls import path

from . import views


app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
+   path('token/', views.CreateTokenView.as_view(), name='token'),
]
```