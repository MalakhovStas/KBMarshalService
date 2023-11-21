from ..loader import dp
from .middlewares import AccessControlMiddleware

if __name__.endswith('middlewares'):
    dp.middleware.setup(AccessControlMiddleware())
