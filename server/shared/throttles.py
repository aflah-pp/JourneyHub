# from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


# class LoginRateThrottle(AnonRateThrottle):
#     rate = "10/hour"


# class PasswordResetRateThrottle(AnonRateThrottle):
#     rate = "3/hour"


# class RegistrationRateThrottle(AnonRateThrottle):
#     rate = "5/hour"


# class JourneysAnonRateThrottle(AnonRateThrottle):
#     rate = "60/minute"


# class JourneyCreateThrottle(UserRateThrottle):
#     rate = "10/hour"


# class UpdateCreateThrottle(UserRateThrottle):
#     rate = "30/hour"


# class CommentCreateThrottle(UserRateThrottle):
#     rate = "30/hour"


# class LikeThrottle(UserRateThrottle):
#     rate = "60/hour"


# class CommentThrottle(UserRateThrottle):
#     rate = "30/hour"


# class ReplyThrottle(UserRateThrottle):
#     rate = "30/hour"


# class SaveJourneyThrottle(UserRateThrottle):
#     rate = "30/hour"


# class SaveUpdateThrottle(UserRateThrottle):
#     rate = "30/hour"


# class SolutionAcceptThrottle(UserRateThrottle):
#     rate = "10/hour"


# class ReportThrottle(UserRateThrottle):
#     rate = "10/day"


# class FeedbackThrottle(UserRateThrottle):
#     rate = "5/hour"


from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    rate = "100/hour"


class PasswordResetRateThrottle(AnonRateThrottle):
    rate = "20/hour"


class RegistrationRateThrottle(AnonRateThrottle):
    rate = "50/hour"


class JourneysAnonRateThrottle(AnonRateThrottle):
    rate = "300/minute"


class JourneyCreateThrottle(UserRateThrottle):
    rate = "100/hour"


class UpdateCreateThrottle(UserRateThrottle):
    rate = "300/hour"


class CommentCreateThrottle(UserRateThrottle):
    rate = "300/hour"


class LikeThrottle(UserRateThrottle):
    rate = "1000/hour"


class CommentThrottle(UserRateThrottle):
    rate = "300/hour"


class ReplyThrottle(UserRateThrottle):
    rate = "300/hour"


class SaveJourneyThrottle(UserRateThrottle):
    rate = "500/hour"


class SaveUpdateThrottle(UserRateThrottle):
    rate = "500/hour"


class SolutionAcceptThrottle(UserRateThrottle):
    rate = "100/hour"


class ReportThrottle(UserRateThrottle):
    rate = "100/day"


class FeedbackThrottle(UserRateThrottle):
    """Rate limit for feedback submissions."""

    rate = "100/hour"
