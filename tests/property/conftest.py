"""Load the qa profile before the property tests run."""

from hypothesis import settings

settings.register_profile("qa", max_examples=500, deadline=None, derandomize=True)
settings.load_profile("qa")
