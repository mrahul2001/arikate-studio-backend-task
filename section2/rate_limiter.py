from .redis_client import redis_client

RATE_LIMIT = 200          # emails
WINDOW_SECONDS = 60       # per minute
KEY = "email_token_bucket"

LUA_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])

local current = redis.call("GET", key)

if not current then
    redis.call("SET", key, limit - 1, "EX", ttl)
    return 1
end

current = tonumber(current)

if current > 0 then
    redis.call("DECR", key)
    return 1
end

return 0
"""

script = redis_client.register_script(LUA_SCRIPT)


def acquire_token():
    """
    Returns True if a token was acquired.
    Returns False if the rate limit has been reached.
    """
    result = script(
        keys=[KEY],
        args=[RATE_LIMIT, WINDOW_SECONDS],
    )

    return result == 1
