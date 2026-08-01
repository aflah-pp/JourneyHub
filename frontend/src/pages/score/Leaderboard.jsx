import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { scoreService } from "@/services/auth";
import { toast } from "sonner";
import { Loader2, Trophy, Medal, Crown } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";

const RANK_COLORS = {
  1: "text-yellow-500",
  2: "text-gray-400",
  3: "text-amber-600",
};

const RANK_ICONS = {
  1: <Crown className="h-5 w-5 text-yellow-500" />,
  2: <Medal className="h-5 w-5 text-gray-400" />,
  3: <Medal className="h-5 w-5 text-amber-600" />,
};

// ---------- Reusable Skeleton ----------
function LeaderboardSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-32" />
      </div>
      <div className="space-y-2">
        {[...Array(10)].map((_, i) => (
          <Skeleton key={i} className="h-16 w-full rounded-xl" />
        ))}
      </div>
    </div>
  );
}

export default function Leaderboard() {
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState([]);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 20;

  const fetchLeaderboard = async (pageNum = 1) => {
    setLoading(true);
    try {
      const params = { page: pageNum, page_size: pageSize };
      const response = await scoreService.getLeaderboard(params);
      const data = response.data;
      const results = data.results || [];

      if (pageNum === 1) {
        setEntries(results);
      } else {
        setEntries((prev) => [...prev, ...results]);
      }

      setTotalCount(data.count || 0);
      setHasNext(!!data.next);
      setPage(pageNum);
    } catch {
      toast.error("Failed to load leaderboard");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchLeaderboard(1);
  }, []);

  const loadMore = () => {
    if (!hasNext || loading) return;
    fetchLeaderboard(page + 1);
  };

  if (loading && entries.length === 0) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <LeaderboardSkeleton />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Trophy className="h-6 w-6 text-yellow-500" />
            Leaderboard
          </h1>
          <p className="text-sm text-muted-foreground">
            {totalCount} builders ranked by total score
          </p>
        </div>
        <Badge variant="outline" className="text-sm">
          Top {totalCount}
        </Badge>
      </div>

      {/* Leaderboard List */}
      {entries.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="py-16 text-center">
            <Trophy className="mx-auto h-12 w-12 text-muted-foreground/40" />
            <p className="mt-4 text-muted-foreground">No entries yet</p>
            <p className="text-sm text-muted-foreground">
              Start building to earn points and climb the ranks!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {entries.map((entry, index) => {
            // ✅ Use rank from backend
            const rank = entry.rank || (page - 1) * pageSize + index + 1;
            const isTop3 = rank <= 3;
            const username = entry.user_username || "Unknown";
            const initial = username?.charAt(0)?.toUpperCase() || "U";

            return (
              <Link
                key={index}
                to={`/profile/${username}`}
                className={`block rounded-xl border bg-card transition-all hover:shadow-md hover:border-primary/30 ${
                  isTop3 ? "border-primary/20 bg-primary/5" : ""
                }`}
              >
                <div className="flex items-center gap-4 p-4">
                  {/* Rank */}
                  <div className="w-10 text-center font-bold">
                    {isTop3 ? (
                      <span className={RANK_COLORS[rank] || "text-muted-foreground"}>
                        {RANK_ICONS[rank] || `#${rank}`}
                      </span>
                    ) : (
                      <span className="text-sm text-muted-foreground">#{rank}</span>
                    )}
                  </div>

                  {/* Avatar - fallback with initials */}
                  <Avatar className="h-10 w-10">
                    <AvatarImage src="" alt={username} />
                    <AvatarFallback>{initial}</AvatarFallback>
                  </Avatar>

                  {/* Username */}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{username}</p>
                    <p className="text-xs text-muted-foreground">
                      Level {entry.level} · {entry.current_streak || 0} day streak
                    </p>
                  </div>

                  {/* Score */}
                  <div className="text-right">
                    <p className="text-xl font-bold">{entry.total_score}</p>
                    <p className="text-xs text-muted-foreground">points</p>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {/* Load More */}
      {hasNext && (
        <div className="flex justify-center pt-4">
          <Button
            variant="outline"
            onClick={loadMore}
            disabled={loading}
            className="w-full max-w-sm"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Loading...
              </>
            ) : (
              "Load more"
            )}
          </Button>
        </div>
      )}
    </div>
  );
}
