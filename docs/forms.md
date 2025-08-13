# Forms Documentation

## Authentication Forms

### User Account Manager Forms

#### Registration Form
```python
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('@')[1]
        if settings.COOPHIVE_DOMAIN_RESTRICTION['ENABLED']:
            if domain != settings.COOPHIVE_DOMAIN_RESTRICTION['ALLOWED_DOMAIN']:
                raise ValidationError("Invalid email domain")
        return email
```

#### Login Form
```python
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))
    
    def confirm_login_allowed(self, user):
        if not user.email_verified:
            raise ValidationError("Please verify your email before logging in.")
```

#### Email Verification Form
```python
class EmailVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6)
    
    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise ValidationError("Verification code must be numeric")
        return code
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

## Form Templates

### Base Form Template
```html
{% extends "_base.html" %}
{% block content %}
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.non_field_errors }}
    {% for field in form %}
    <div class="form-group">
        {{ field.label_tag }}
        {{ field }}
        {{ field.errors }}
        {% if field.help_text %}
        <small class="form-text text-muted">{{ field.help_text }}</small>
        {% endif %}
    </div>
    {% endfor %}
    <button type="submit" class="btn btn-primary">Submit</button>
</form>
{% endblock %}
```
