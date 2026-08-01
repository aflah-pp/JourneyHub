import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { notificationService } from "@/services/auth";
import { toast } from "sonner";
import {
  Loader2,
  Bell,
  CheckCheck,
  Heart,
  MessageCircle,
  UserPlus,
  Check,
  TrendingUp,
  ArrowRight,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const NOTIFICATION_ICONS = {
  LIKE: Heart,
  COMMENT: MessageCircle,
  COMMENT_REPLY: MessageCircle,
  FOLLOW: UserPlus,
  ACCEPTED_SOLUTION: Check,
  MILESTONE: TrendingUp,
};

const NOTIFICATION_COLORS = {
  LIKE: "text-red-400",
  COMMENT: "text-blue-400",
  COMMENT_REPLY: "text-blue-400",
  FOLLOW: "text-green-400",
  ACCEPTED_SOLUTION: "text-purple-400",
  MILESTONE: "text-yellow-400",
};

const PAGE_PADDING = "p-4 md:p-6 lg:p-8";

export default function Notifications() {
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [pageSize] = useState(20);

  const fetchNotifications = useCallback(
    async (pageNum) => {
      try {
        const response = await notificationService.listNotifications(pageNum, pageSize);
        const data = response.data;
        const results = data.results || [];

        if (pageNum === 1) {
          setNotifications(results);
        } else {
          setNotifications((prev) => [...prev, ...results]);
        }

        setHasNext(!!data.next);
        setPage(pageNum);
        // eslint-disable-next-line no-unused-vars
      } catch (err) {
        toast.error("Failed to load notifications");
      }
    },
    [pageSize],
  );

  const fetchUnreadCount = useCallback(async () => {
    try {
      const response = await notificationService.getUnreadCount();
      setUnreadCount(response.data?.unread_count || 0);
      // eslint-disable-next-line no-unused-vars
    } catch (err) {
      // Silently fail
    }
  }, []);

  useEffect(() => {
    const loadInitial = async () => {
      setLoading(true);
      await Promise.all([fetchNotifications(1), fetchUnreadCount()]);
      setLoading(false);
    };
    loadInitial();
  }, [fetchNotifications, fetchUnreadCount]);

  const loadMore = async () => {
    if (loadingMore || !hasNext) return;
    setLoadingMore(true);
    await fetchNotifications(page + 1);
    setLoadingMore(false);
  };

  const handleMarkAsRead = async (id) => {
    try {
      await notificationService.updateNotification(id, { is_read: true });
      setNotifications((prev) =>
        prev.map((n) =>
          n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n,
        ),
      );
      setUnreadCount((prev) => Math.max(prev - 1, 0));
      // eslint-disable-next-line no-unused-vars
    } catch (err) {
      toast.error("Failed to mark notification as read");
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, is_read: true, read_at: new Date().toISOString() })),
      );
      setUnreadCount(0);
      toast.success("All notifications marked as read");
      // eslint-disable-next-line no-unused-vars
    } catch (err) {
      toast.error("Failed to mark all as read");
    }
  };

  if (loading) {
    return (
      <div className={`mx-auto max-w-2xl w-full space-y-4 ${PAGE_PADDING}`}>
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <div className={`mx-auto max-w-2xl w-full ${PAGE_PADDING}`}>
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-primary/10 p-2 text-primary">
            <Bell className="h-5 w-5" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Notifications</h1>
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="ml-1 font-medium"
              aria-label={`${unreadCount} unread notifications`}
            >
              {unreadCount}
            </Badge>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleMarkAllAsRead}
          disabled={unreadCount === 0}
          className="gap-1.5 text-xs"
        >
          <CheckCheck className="h-4 w-4" />
          Mark all read
        </Button>
      </div>

      {notifications.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="py-16 text-center">
            <div className="mx-auto w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
              <Bell className="h-8 w-8 text-muted-foreground/40" />
            </div>
            <p className="text-lg font-medium text-muted-foreground">No notifications</p>
            <p className="text-sm text-muted-foreground mt-1">
              When you get notifications, they'll appear here
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="space-y-2">
            {notifications.map((notification) => {
              const Icon = NOTIFICATION_ICONS[notification.notification_type] || Bell;
              const iconColor =
                NOTIFICATION_COLORS[notification.notification_type] || "text-muted-foreground";

              return (
                <Card
                  key={notification.id}
                  className={`transition-all duration-200 hover:shadow-md ${
                    !notification.is_read
                      ? "border-l-4 border-l-primary bg-primary/5"
                      : "hover:border-muted-foreground/20"
                  }`}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <Link to={`/profile/${notification.actor?.username}`} className="shrink-0">
                        <Avatar className="h-10 w-10 ring-1 ring-border/50">
                          <AvatarImage
                            src={notification.actor?.avatar_url}
                            alt={notification.actor?.username}
                          />
                          <AvatarFallback className="text-sm font-medium">
                            {notification.actor?.username?.charAt(0)?.toUpperCase() || "U"}
                          </AvatarFallback>
                        </Avatar>
                      </Link>

                      <div className="flex-1 min-w-0">
                        <div className="min-w-0">
                          <Link
                            to={`/profile/${notification.actor?.username}`}
                            className="font-semibold text-sm hover:underline"
                          >
                            {notification.actor?.username}
                          </Link>
                          <span className="text-sm text-muted-foreground">
                            {" "}
                            {notification.title?.replace(/^[^ ]+ /, "")}
                          </span>
                        </div>

                        <p className="text-sm text-muted-foreground line-clamp-2 mt-0.5">
                          {notification.body}
                        </p>

                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-xs text-muted-foreground">
                          <span>
                            {formatDistanceToNow(new Date(notification.created_at), {
                              addSuffix: true,
                            })}
                          </span>
                          <span className="w-1 h-1 rounded-full bg-muted-foreground/30" />
                          <span className="capitalize">
                            {notification.notification_type?.toLowerCase().replace("_", " ")}
                          </span>
                          {notification.target_detail && (
                            <>
                              <span className="w-1 h-1 rounded-full bg-muted-foreground/30" />
                              <Link
                                to={`/journeys/${notification.target_id}`}
                                className="inline-flex items-center gap-1 text-primary hover:underline font-medium"
                              >
                                View
                                <ArrowRight className="h-3 w-3" />
                              </Link>
                            </>
                          )}
                        </div>
                      </div>

                      <div className="flex flex-col items-center gap-2 shrink-0">
                        {!notification.is_read && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 cursor-pointer rounded-full transition-colors hover:bg-blue-100 dark:hover:bg-blue-900/30"
                            onClick={() => handleMarkAsRead(notification.id)}
                            aria-label="Mark as read"
                            title="Mark as read"
                          >
                            <Check className="h-4 w-4 text-muted-foreground hover:text-primary" />
                          </Button>
                        )}
                        <div
                          className={`h-7 w-7 rounded-full flex items-center justify-center bg-current/10 ${iconColor}`}
                        >
                          <Icon className="h-3.5 w-3.5" />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {hasNext && (
            <div className="flex justify-center pt-6">
              <Button
                variant="outline"
                onClick={loadMore}
                disabled={loadingMore}
                className="w-full max-w-sm gap-2"
              >
                {loadingMore ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  "Load more"
                )}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
