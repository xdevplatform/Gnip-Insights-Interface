
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

class AudienceApiException(InsightsApiException):
    pass
class NoSegmentsFoundException(AudienceApiException):
    pass
class AudienceTooSmallException(AudienceApiException):
    pass
class SegmentDeleteException(AudienceApiException):
    pass
class SegmentQueryException(AudienceApiException): 
    pass
class SegmentCreateException(AudienceApiException): 
    pass
class SegmentPostIdsException(AudienceApiException):
    pass
class AudiencePostException(AudienceApiException):
    pass
class AudienceInfoException(AudienceApiException):
    pass
