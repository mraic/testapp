from .development import Development
from .test import Test
from .production import Production

environments = {
    'development': Development,
    'test': Test,
    'production': Production
}
