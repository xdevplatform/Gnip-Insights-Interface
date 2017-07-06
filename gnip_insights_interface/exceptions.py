
class InsightsApiException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
class CredentialsException(InsightsApiException):
    pass

class EngagementApiException(InsightsApiException):
    pass
class DateRangeException(EngagementApiException):
    pass

