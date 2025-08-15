from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css):
    """Add CSS classes to form fields while preserving existing attributes."""
    return field.as_widget(attrs={**field.field.widget.attrs, "class": css})


@register.filter(name="add_attrs")
def add_attrs(field, attrs_string):
    """Add multiple attributes to form fields.
    
    Usage: {{ form.field|add_attrs:"placeholder=Enter text,class=form-control" }}
    """
    attrs = {}
    for attr in attrs_string.split(','):
        key, value = attr.split('=', 1)
        attrs[key.strip()] = value.strip()
    
    return field.as_widget(attrs={**field.field.widget.attrs, **attrs})


@register.filter(name="field_type")
def field_type(field):
    """Get the field type name."""
    return field.field.__class__.__name__


@register.filter(name="is_required")
def is_required(field):
    """Check if field is required."""
    return field.field.required
