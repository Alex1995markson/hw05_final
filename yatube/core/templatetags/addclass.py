from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='addclass')
def addclass(field, class_attr):
    return field.as_widget(attrs={'class': class_attr})


@register.filter(name="extra_addclass")
def extra_addclass(field, class_attr):
    str_tag = f'<span class="{str(class_attr)}">' + field + '</span>'
    return mark_safe(str_tag)


@register.filter(name="replace_paragraph")
def replace_paragraph(field):
    # необходимо сначала разбить на пробелы
    # получить [] => обернуть его в параграф
    str_tags = re.split(r"^\s+|\n|\r|\s+$", str)
    return mark_safe(str_tags)
