from django import template

register = template.Library()


base = 'https:////www.imdb.com//find?q='

@register.filter
def mul(val):
    return val*10


@register.filter
def more(val):
    return base+val