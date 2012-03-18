from handlers import WebApiHandler

urls = (
    (r'^/api/(?:(.+?)/)?(?:(.+?)/)?$', WebApiHandler),
)
