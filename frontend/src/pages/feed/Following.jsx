import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { feedService, reactionService } from "@/services/auth";
import { toast } from "sonner";
import {
  Loader2,
  Heart,
  MessageCircle,
  Bookmark,
  BookmarkCheck,
  Calendar,
  Tag,
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { FeedSkeleton } from "@/components/feed/FeedSkelton";

export default function FeedFollowing() {
  const { user, isAuthenticated } = useAuthStore();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [nextCursor, setNextCursor] = useState(null);
  const [hasNext, setHasNext] = useState(false);
  const [pageSize] = useState(30);

  const fetchFeed = useCallback(
    async (cursor = null) => {
      try {
        const response = await feedService.followingFeed(cursor, pageSize);
        const data = response.data;
        const results = data.results || [];
        const nextCursorValue = data.next_cursor || null;

        if (cursor) {
          setItems((prev) => [...prev, ...results]);
        } else {
          setItems(results);
        }

        setNextCursor(nextCursorValue);
        setHasNext(data.has_next || false);
        // eslint-disable-next-line no-unused-vars
      } catch (err) {
        toast.error("Failed to load feed");
      }
    },
    [pageSize],
  );

  useEffect(() => {
    if (!isAuthenticated) {
      toast.info("Please login to see your following feed");
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLoading(false);
      return;
    }

    const loadFeed = async () => {
      setLoading(true);
      await fetchFeed();
      setLoading(false);
    };
    loadFeed();
  }, [fetchFeed, isAuthenticated]);

  const loadMore = async () => {
    if (loadingMore || !hasNext || !nextCursor) return;
    setLoadingMore(true);
    await fetchFeed(nextCursor);
    setLoadingMore(false);
  };

  const handleLike = async (updateId, isLiked) => {
    try {
      setItems((prev) =>
        prev.map((item) =>
          item.id === updateId
            ? {
                ...item,
                is_liked_by_me: !item.is_liked_by_me,
                like_count: item.is_liked_by_me ? item.like_count - 1 : item.like_count + 1,
              }
            : item,
        ),
      );

      if (isLiked) {
        await reactionService.toggleUnLike(updateId);
        toast.success("UnLiked the update");
      } else {
        await reactionService.toggleLike(updateId);
        toast.success("Liked the update");
      }
      // eslint-disable-next-line no-unused-vars
    } catch (err) {
      toast.error("Failed to toggle like");
      await fetchFeed();
    }
  };

  const handleSave = async (updateId, isSaved) => {
    try {
      setItems((prev) =>
        prev.map((item) =>
          item.id === updateId
            ? {
                ...item,
                is_saved_by_me: !item.is_saved_by_me,
              }
            : item,
        ),
      );

      if (isSaved) {
        await reactionService.unsaveUpdate(updateId);
        toast.success("Update removed from Saves");
      } else {
        await reactionService.toggleSave(updateId);
        toast.success("Saved the update");
      }
      // eslint-disable-next-line no-unused-vars
    } catch (err) {
      toast.error("Failed to toggle save");
      await fetchFeed();
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl space-y-4 px-4 py-8">
        {[...Array(3)].map((_, i) => (
          <FeedSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-lg font-medium">Please login</p>
            <p className="text-sm text-muted-foreground">
              You need to be logged in to see your following feed
            </p>
            <Button asChild className="mt-4">
              <Link to="/login">Login</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">No posts from followed users yet</p>
            <p className="text-sm text-muted-foreground">
              Follow some users to see their updates here
            </p>
            <Button asChild className="mt-4">
              <Link to="/explore/users">Explore Users</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4 px-4 py-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Following Feed</h1>
        <Badge variant="outline">{items.length} posts</Badge>
      </div>

      {items.map((item) => (
        <FeedItem
          key={item.id}
          item={item}
          currentUser={user}
          onLike={handleLike}
          onSave={handleSave}
        />
      ))}

      {hasNext && (
        <div className="flex justify-center pt-4">
          <Button
            variant="outline"
            onClick={loadMore}
            disabled={loadingMore}
            className="w-full max-w-sm"
          >
            {loadingMore ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Loading...
              </>
            ) : (
              "Load More"
            )}
          </Button>
        </div>
      )}

      {!hasNext && items.length > 0 && (
        <p className="text-center text-sm text-muted-foreground py-4">
          You've reached the end of the feed
        </p>
      )}
    </div>
  );
}

// eslint-disable-next-line no-unused-vars
function FeedItem({ item, currentUser, onLike, onSave }) {
  return (
    <Card className="overflow-hidden rounded-xl border bg-card transition-all hover:shadow-md">
      <CardContent className="p-5 space-y-4">
        <div className="flex items-start justify-between">
          <Link
            to={`/profile/${item.author?.username}`}
            className="flex items-center gap-3 min-w-0"
          >
            <Avatar className="h-10 w-10 shrink-0">
              <AvatarImage src={item.author?.avatar_url} alt={item.author?.username} />
              <AvatarFallback>
                {item.author?.username?.charAt(0)?.toUpperCase() || "U"}
              </AvatarFallback>
            </Avatar>
            <div className="min-w-0">
              <p className="truncate font-medium hover:underline">{item.author?.username}</p>
              <p className="truncate text-xs text-muted-foreground">{item.journey_title}</p>
            </div>
          </Link>
          <Badge variant="outline" className="text-xs shrink-0 ml-2">
            <Calendar className="mr-1 h-3 w-3" />
            {new Date(item.created_at).toLocaleDateString()}
          </Badge>
        </div>

        <Link to={`/journeys/${item.journey_id}/updates/${item.id}`}>
          <h3 className="text-lg font-semibold hover:text-primary transition-colors">
            {item.title}
          </h3>
        </Link>

        {item.description && (
          <div
            className="prose prose-sm max-w-none text-muted-foreground line-clamp-3"
            dangerouslySetInnerHTML={{ __html: item.description }}
          />
        )}

        {item.images && item.images.length > 0 && (
          <div
            className={`grid gap-2 ${
              item.images.length === 1
                ? "grid-cols-1"
                : item.images.length === 2
                  ? "grid-cols-2"
                  : "grid-cols-2"
            }`}
          >
            {item.images.slice(0, 4).map((image, idx) => (
              <div
                key={image.id}
                className={`relative overflow-hidden rounded-lg bg-muted ${
                  idx === 0 && item.images.length === 3 ? "row-span-2" : ""
                }`}
                style={{ paddingBottom: "56.25%" }}
              >
                <img
                  src={image.cloudinary_url}
                  alt={`Update image ${idx + 1}`}
                  className="absolute inset-0 h-full w-full object-cover"
                  loading="lazy"
                />
                {idx === 3 && item.images.length > 4 && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/50 text-white font-bold text-lg">
                    +{item.images.length - 4}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {item.tags && item.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {item.tags.map((tag) => (
              <Badge key={tag.id} variant="secondary" className="text-xs rounded-full">
                <Tag className="mr-1 h-3 w-3" />
                {tag.name}
              </Badge>
            ))}
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {item.milestone_badge && (
            <Badge
              className={`text-xs ${
                item.milestone_badge.color === "blue" ? "bg-blue-500" : "bg-green-500"
              }`}
            >
              {item.milestone_badge.label}
            </Badge>
          )}
          {item.help_needed_badge && (
            <Badge className="bg-orange-500 text-xs">{item.help_needed_badge.label}</Badge>
          )}
        </div>

        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              className="gap-1.5"
              onClick={() => onLike(item.id, item.is_liked_by_me)}
            >
              <Heart
                className={`h-4 w-4 ${item.is_liked_by_me ? "fill-red-500 text-red-500" : ""}`}
              />
              <span>{item.like_count}</span>
            </Button>

            <Button variant="ghost" size="sm" className="gap-1.5" asChild>
              <Link to={`/journeys/${item.journey_id}/updates/${item.id}`}>
                <MessageCircle className="h-4 w-4" />
                <span>{item.comment_count}</span>
              </Link>
            </Button>
          </div>

          <Button
            variant="ghost"
            size="sm"
            className="gap-1.5"
            onClick={() => onSave(item.id, item.is_saved_by_me)}
          >
            {item.is_saved_by_me ? (
              <BookmarkCheck className="h-4 w-4 text-primary" />
            ) : (
              <Bookmark className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
