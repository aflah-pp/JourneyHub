from rest_framework import permissions

from audit.models import ReportedItem
from journey.models import Journey, JourneyUpdate


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows read-only access for everyone, but write access only to the owner.
    Use this for generic object-level permissions.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        if hasattr(obj, "author"):
            return obj.author == request.user

        return False


class IsJourneyOwner(permissions.BasePermission):
    """
    Allows only the owner of the journey to modify it.
    Works with Journey, JourneyUpdate, and related objects.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Journey):
            return obj.owner == request.user

        if isinstance(obj, JourneyUpdate):
            return obj.journey.owner == request.user

        if hasattr(obj, "journey") and hasattr(obj.journey, "owner"):
            return obj.journey.owner == request.user

        return False


class CanViewJourney(permissions.BasePermission):
    """
    Controls visibility based on journey.visibility.
    Handles PUBLIC, FOLLOWERS_ONLY, and PRIVATE visibility levels.
    """

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, (Journey, JourneyUpdate)):
            return True

        if isinstance(obj, Journey):
            journey = obj
        else:
            journey = obj.journey

        if journey.is_deleted:
            return False

        visibility = getattr(obj, "visibility", None) or journey.visibility

        if visibility == Journey.Visibility.PUBLIC:
            return True

        if visibility == Journey.Visibility.FOLLOWERS:
            if request.user == journey.owner:
                return True
            if not request.user.is_authenticated:
                return False
            return request.user.follower_relations.filter(
                following=journey.owner
            ).exists()

        if visibility == Journey.Visibility.PRIVATE:
            return request.user == journey.owner

        return False


class CanViewJourneyUpdate(permissions.BasePermission):
    """
    Controls visibility for journey updates specifically.
    Checks both update-level visibility and journey-level visibility.
    """

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, JourneyUpdate):
            return True

        journey = obj.journey

        if journey.is_deleted:
            return False

        visibility = obj.visibility or journey.visibility

        if visibility == Journey.Visibility.PUBLIC:
            return True

        if visibility == Journey.Visibility.FOLLOWERS:
            if request.user == journey.owner:
                return True
            if not request.user.is_authenticated:
                return False
            return request.user.follower_relations.filter(
                following=journey.owner
            ).exists()

        if visibility == Journey.Visibility.PRIVATE:
            return request.user == journey.owner

        return False


class IsUpdateOwnerOrJourneyOwner(permissions.BasePermission):
    """
    Allows access if user is either the update's journey owner or the update author.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, JourneyUpdate):
            return obj.journey.owner == request.user
        return False


class CanLikeUpdate(permissions.BasePermission):
    """
    Allows a user to like/unlike an update only if:
    - User is authenticated
    - The update is not deleted
    - The update is visible to the user
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, JourneyUpdate):
            return False

        if obj.is_deleted:
            return False

        return CanViewJourneyUpdate().has_object_permission(request, view, obj)


class CanCreateComment(permissions.BasePermission):
    """
    Allows creating a comment only if:
    - User is authenticated
    - The update is not deleted
    - The update is visible to the user
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, JourneyUpdate):
            return True

        if obj.is_deleted:
            return False

        return CanViewJourneyUpdate().has_object_permission(request, view, obj)


class IsCommentAuthor(permissions.BasePermission):
    """
    Allows a user to modify/delete only their own comments.
    Also checks that the comment is not deleted.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if obj.__class__.__name__ == "Comment":
            if obj.is_deleted:
                return False
            return obj.user == request.user

        return False


class CanCreateReply(permissions.BasePermission):
    """
    Allows creating a reply only if:
    - User is authenticated
    - The comment is not deleted
    - The parent update is visible
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if obj.__class__.__name__ == "Comment":
            if obj.is_deleted:
                return False

            return CanViewJourneyUpdate().has_object_permission(
                request, view, obj.journey_update
            )

        return False


class IsReplyAuthor(permissions.BasePermission):
    """
    Allows a user to modify/delete only their own replies.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if obj.__class__.__name__ == "CommentReply":
            if obj.is_deleted:
                return False
            return obj.user == request.user

        return False


class CanAcceptSolution(permissions.BasePermission):
    """
    Allows accepting a solution only if:
    - User is the journey owner
    - The update is not deleted
    - The update has help_needed=True
    - No solution has been accepted yet
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, JourneyUpdate):
            return False

        if obj.journey.owner != request.user:
            return False

        if obj.is_deleted:
            return False

        if not obj.help_needed:
            return False

        if hasattr(obj, "accepted_solution") and obj.accepted_solution:
            return False

        return True


class CanRemoveAcceptedSolution(permissions.BasePermission):
    """
    Allows removing an accepted solution only if:
    - User is the journey owner
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, JourneyUpdate):
            return False

        return obj.journey.owner == request.user


class CanSaveJourney(permissions.BasePermission):
    """
    Allows a user to save/unsave a journey only if:
    - User is authenticated
    - The journey is not deleted
    - The journey is visible to the user (PUBLIC, FOLLOWERS, or owned)
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Journey):
            return False

        if obj.is_deleted:
            return False

        if obj.visibility == Journey.Visibility.PRIVATE:
            return obj.owner == request.user

        return True


class IsSavedJourneyOwner(permissions.BasePermission):
    """
    Allows a user to view/delete only their own saved journeys.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if obj.__class__.__name__ == "SavedJourney":
            return obj.user == request.user

        return False


class CanSaveUpdate(permissions.BasePermission):
    """
    Allows a user to save/unsave an update only if:
    - User is authenticated
    - The update is not deleted
    - The update is visible to the user
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, JourneyUpdate):
            return False

        if obj.is_deleted:
            return False

        return CanViewJourneyUpdate().has_object_permission(request, view, obj)


class IsSavedUpdateOwner(permissions.BasePermission):
    """
    Allows a user to view/delete only their own saved updates.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if obj.__class__.__name__ == "SavedUpdate":
            return obj.user == request.user
        return False


class IsNotificationRecipient(permissions.BasePermission):
    """
    Allows a user to view/modify only their own notifications.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if obj.__class__.__name__ == "Notification":
            return obj.recipient == request.user

        return False


class CanManageTags(permissions.BasePermission):
    """
    Allows managing tags only if:
    - User is the journey owner
    - The update is not deleted
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, JourneyUpdate):
            return False

        if obj.is_deleted:
            return False

        return obj.journey.owner == request.user


class CanManageImages(permissions.BasePermission):
    """
    Allows managing images only if:
    - User is the journey owner
    - The update is not deleted
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, JourneyUpdate):
            return False

        if obj.is_deleted:
            return False

        return obj.journey.owner == request.user


class IsModerator(permissions.BasePermission):
    """
    Allows access only to users with moderator/staff privileges.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsReporterOrModerator(permissions.BasePermission):
    """
    Allows access if the user is either the reporter or a moderator (staff).
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, ReportedItem):
            return obj.reporter == request.user or request.user.is_staff
        return False


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Allows access if user is either the owner or a moderator.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user") and obj.user == request.user:
            return True
        if hasattr(obj, "owner") and obj.owner == request.user:
            return True
        if hasattr(obj, "author") and obj.author == request.user:
            return True

        return request.user.is_staff


class IsAuthenticatedAndVerified(permissions.BasePermission):
    """
    Allows access only if user is authenticated and email verified.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_verified
            and not request.user.is_suspended
        )


def check_journey_visibility(journey, user):
    """
    Helper function to check if a journey is visible to a user.
    Can be used in views and other permissions.
    """
    if not journey or journey.is_deleted:
        return False

    if journey.visibility == Journey.Visibility.PUBLIC:
        return True

    if journey.visibility == Journey.Visibility.FOLLOWERS:
        if not user or not user.is_authenticated:
            return False
        if user == journey.owner:
            return True
        return user.follower_relations.filter(following=journey.owner).exists()

    if journey.visibility == Journey.Visibility.PRIVATE:
        return user == journey.owner

    return False


def check_update_visibility(update, user):
    """
    Helper function to check if an update is visible to a user.
    Considers both update-level and journey-level visibility.
    """
    if not update or update.is_deleted:
        return False

    journey = update.journey

    if journey.is_deleted:
        return False

    visibility = update.visibility or journey.visibility

    if visibility == Journey.Visibility.PUBLIC:
        return True

    if visibility == Journey.Visibility.FOLLOWERS:
        if not user or not user.is_authenticated:
            return False
        if user == journey.owner:
            return True
        return user.follower_relations.filter(following=journey.owner).exists()

    if visibility == Journey.Visibility.PRIVATE:
        return user == journey.owner

    return False
