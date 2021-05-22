from django import template

register = template.Library()


@register.filter(name='censor')
def censor(value):
    banned_words = ['негатив', 'депрессия', 'обзывательство']
    for c in banned_words:
        value = value.replace(c, len(c) * '*')
        return value
