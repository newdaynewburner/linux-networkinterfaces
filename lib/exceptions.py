"""
lib/exceptions.py

Custom exceptions defined here
"""

class GetAttributeError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SetAttributeError(Exception):
    def __init__(self, message):
        super().__init__(message)

class StateChangeError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ModeChangeError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ChannelChangeError(Exception):
    def __init__(self, message):
        super().__init__(message)
