from jinja2.ext import i18n

def environment(**options):
    env = Environment(**options)
    env.add_extension(i18n)
    return env