from src.middleware import RequestIDMiddleware


def test_request_id_middleware_class():
    from fastapi import FastAPI
    app = FastAPI()
    middleware = RequestIDMiddleware(app)
    assert middleware is not None

def test_rate_limit_middleware_class():
    from fastapi import FastAPI

    from src.middleware import RateLimitMiddleware
    app = FastAPI()
    middleware = RateLimitMiddleware(app, max_requests=10, window_seconds=5)
    assert middleware.max_requests == 10
