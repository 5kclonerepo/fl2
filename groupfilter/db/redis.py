# Copyright (C) 2024 @jithumon

import redis


class NamespacedRedis(redis.Redis):
    def __init__(self, bot_token: str, *args, **kwargs):
        self.namespace = f"bot:{bot_token}:"
        super().__init__(*args, **kwargs)

    def _apply_namespace(self, key):
        """Private method to apply namespace to the key."""
        return self.namespace + key

    def set(self, name, value, *args, **kwargs):
        """Override set method to apply namespace."""
        return super().set(self._apply_namespace(name), value, *args, **kwargs)

    def get(self, name, *args, **kwargs):
        """Override get method to apply namespace."""
        return super().get(self._apply_namespace(name), *args, **kwargs)
