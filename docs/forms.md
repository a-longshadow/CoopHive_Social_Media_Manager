# Forms Documentation

## Authentication Forms

### User Account Manager Forms

#### Registration Form (TaskForge-style)
```python
class RegisterForm(forms.Form):
    """Registration form with TaskForge field structure and domain validation."""
    email = forms.EmailField()
    name = forms.CharField(required=False, max_length=150, label="Full name")
    username = forms.CharField(required=False, max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["placeholder"] = "yourname@coophive.network"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm password"
        self.fields["password1"].widget.attrs["placeholder"] = "Create a strong password"
        self.fields["password2"].widget.attrs["placeholder"] = "Re-enter password"
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"
        
        # Set default CSS classes for all fields
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class", "w-full border border-gray-300 rounded p-2"
            )

        self.fields["name"].widget.attrs["placeholder"] = "Your full name (optional)"
        self.fields["username"].widget.attrs["placeholder"] = "username (optional)"

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        _validate_domain(email)
        if User.objects.filter(email=email).exists():
            raise ValidationError("User with this e-mail already exists")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")
        
        return cleaned_data
```

#### Login Form (Email/Username Support)
```python
class LoginForm(AuthenticationForm):
    """Custom login form supporting both username and email login."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize the username field to indicate it accepts email too
        self.fields["username"].label = "Username or Email"
        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Enter your username or email",
                "class": "w-full border border-gray-300 rounded p-2",
            }
        )
        
        # Update password field
        self.fields["password"].widget.attrs.update(
            {"class": "w-full border border-gray-300 rounded p-2"}
        )
```

#### Verification Forms
```python
class CodeForm(forms.Form):
    """Form for entering 4-digit verification codes."""
    code = forms.CharField(max_length=4, min_length=4)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code"].widget.attrs["placeholder"] = "1234"
        self.fields["code"].widget.attrs["class"] = "w-full text-center text-3xl font-mono tracking-widest border border-gray-300 rounded p-2"

    def clean_code(self):
        code = self.cleaned_data["code"]
        if not code.isdigit():
            raise ValidationError("Code must contain only digits")
        return code

class GoogleVerificationForm(forms.Form):
    """Form for Google OAuth verification codes."""
    code = forms.CharField(max_length=4, min_length=4)

    def clean_code(self):
        code = self.cleaned_data["code"]
        if not code.isdigit():
            raise ValidationError("Code must contain only digits")
        return code

class PasswordResetRequestForm(forms.Form):
    """Form for requesting a password reset."""
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "w-full border border-gray-300 rounded p-2"}
        )
    )

class PasswordResetForm(forms.Form):
    """Form for setting a new password after reset."""
    code = forms.CharField(
        label="Reset Code",
        max_length=4,
        min_length=4,
        widget=forms.TextInput(
            attrs={
                "class": "w-full text-center font-mono text-2xl border border-gray-300 rounded p-2",
                "placeholder": "0000"
            }
        ),
    )
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={"class": "w-full border border-gray-300 rounded p-2"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={"class": "w-full border border-gray-300 rounded p-2"}
        ),
    )
```

## Social Media Post Forms

### Base Post Form
```python
class BasePostForm(forms.ModelForm):
    schedule_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(
        attrs={'type': 'datetime-local'}
    ))
    media_files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )
    
    class Meta:
        abstract = True
        fields = ['content', 'schedule_time', 'media_files']
```

### LinkedIn Forms

#### LinkedIn Post Form
```python
class LinkedInPostForm(BasePostForm):
    article_title = forms.CharField(max_length=255, required=False)
    article_url = forms.URLField(required=False)
    
    class Meta(BasePostForm.Meta):
        model = LinkedInPost
        fields = BasePostForm.Meta.fields + ['article_title', 'article_url']
```

### Twitter Forms

#### Tweet Form
```python
class TweetForm(BasePostForm):
    in_reply_to = forms.CharField(required=False)
    is_thread = forms.BooleanField(required=False)
    
    class Meta(BasePostForm.Meta):
        model = Tweet
        fields = BasePostForm.Meta.fields + ['in_reply_to', 'is_thread']
```

### Farcaster Forms

#### Cast Form
```python
class CastForm(BasePostForm):
    parent_hash = forms.CharField(required=False)
    
    class Meta(BasePostForm.Meta):
        model = Cast
        fields = BasePostForm.Meta.fields + ['parent_hash']
```

### Bluesky Forms

#### Bluesky Post Form
```python
class BlueskyPostForm(BasePostForm):
    reply_to = forms.CharField(required=False)
    
    class Meta(BasePostForm.Meta):
        model = BlueskyPost
        fields = BasePostForm.Meta.fields + ['reply_to']
```

## Media Forms

### Media Upload Form
```python
class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ['file', 'type', 'alt_text']
        
    def clean_file(self):
        file = self.cleaned_data['file']
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise ValidationError("File size must be under 10MB")
        return file
```

## Form Best Practices

1. Validation
```python
def clean_field(self):
    data = self.cleaned_data['field']
    # Validation logic
    return data
```

2. File Handling
```python
def handle_uploaded_file(self, file):
    with default_storage.open('path/to/file', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
```

3. Custom Widgets
```python
class CustomDateTimeWidget(forms.DateTimeInput):
    input_type = 'datetime-local'
    def __init__(self, attrs=None):
        super().__init__(attrs={'class': 'form-control', **(attrs or {})})
```

4. Form Mixins
```python
class TimestampFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        if 'schedule_time' in cleaned_data:
            if cleaned_data['schedule_time'] < timezone.now():
                raise ValidationError("Schedule time must be in the future")
        return cleaned_data
```

## Template Tags

### Custom Form Tags (`user_account_manager/templatetags/form_tags.py`)
```python
from django import template

register = template.Library()

@register.filter(name="add_class")
def add_class(field, css):
    """Add CSS classes to form fields while preserving existing attributes."""
    return field.as_widget(attrs={**field.field.widget.attrs, "class": css})

@register.filter(name="add_attrs")
def add_attrs(field, attrs_string):
    """Add multiple attributes to form fields."""
    attrs = {}
    for attr in attrs_string.split(','):
        key, value = attr.split('=', 1)
        attrs[key.strip()] = value.strip()
    
    return field.as_widget(attrs={**field.field.widget.attrs, **attrs})
```

## Modern Form Templates

### TaskForge-Style Authentication Templates

#### Key Features:
- **Modern TaskForge styling** with clean white cards and subtle shadows
- **Google OAuth integration** with proper SVG icons
- **Password visibility toggles** with JavaScript
- **Responsive design** that works on all devices
- **Toastify notifications** for user feedback
- **Gradient buttons** and modern typography

#### Template Structure:
- Uses `{% load form_tags %}` for clean form styling
- Extends modern `base.html` with TaskForge background (#F5F7FB)
- Implements `add_class` filter for CSS application
- Includes JavaScript for password toggle functionality
