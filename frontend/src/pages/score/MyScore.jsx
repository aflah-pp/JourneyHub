import { useEffect, useState } from "react";

import { scoreService } from "@/services/auth";
import { toast } from "sonner";
import {
  Award,
  TrendingUp,
  Flame,
  Trophy,
  Star,
  BarChart3,
  ChevronRight,
  Loader2,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

function ScoreSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-32 rounded-xl" />
        ))}
      </div>
      <Skeleton className="h-48 rounded-xl" />
      <div className="grid gap-4 sm:grid-cols-2">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-xl" />
        ))}
      </div>
    </div>
  );
}

export default function MyScore() {
  const [loading, setLoading] = useState(true);
  const [score, setScore] = useState(null);
  const [rank, setRank] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [fullHistory, setFullHistory] = useState([]);
  const [historyPage, setHistoryPage] = useState(1);
  const [historyHasMore, setHistoryHasMore] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const pageSize = 20;

  useEffect(() => {
    const fetchScoreData = async () => {
      setLoading(true);
      try {
        const [scoreRes, rankRes, historyRes] = await Promise.all([
          scoreService.getMyScore(),
          scoreService.getMyRank(),
          scoreService.getScoreHistory({ page_size: 5 }),
        ]);

        setScore(scoreRes.data);
        setRank(rankRes.data);
        setHistory(historyRes.data?.results || []);
      } catch {
        toast.error("Failed to load score data");
      } finally {
        setLoading(false);
      }
    };

    fetchScoreData();
  }, []);

  // Fetch full history when dialog opens
  const fetchFullHistory = async (page = 1, append = false) => {
    setHistoryLoading(true);
    try {
      const response = await scoreService.getScoreHistory({
        page_size: pageSize,
        page,
      });
      const results = response.data?.results || [];
      const next = response.data?.next || null;

      if (append) {
        setFullHistory((prev) => [...prev, ...results]);
      } else {
        setFullHistory(results);
      }

      setHistoryHasMore(!!next);
      setHistoryPage(page);
    } catch {
      toast.error("Failed to load history");
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleDialogOpen = (open) => {
    setHistoryDialogOpen(open);
    if (open && fullHistory.length === 0) {
      fetchFullHistory(1, false);
    }
  };

  const loadMoreHistory = () => {
    if (historyLoading || !historyHasMore) return;
    fetchFullHistory(historyPage + 1, true);
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <ScoreSkeleton />
      </div>
    );
  }

  if (!score) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 text-center">
        <Award className="mx-auto h-12 w-12 text-muted-foreground/40" />
        <p className="mt-4 text-muted-foreground">No score data available.</p>
      </div>
    );
  }

  const levelProgress = (score.experience_points / score.next_level_xp) * 100;

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8">

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">My Builder Score</h1>
          <p className="text-sm text-muted-foreground">Track your progress and engagement</p>
        </div>
        {rank && (
          <Badge variant="outline" className="text-sm">
            #{rank.rank} of {rank.total_users}
          </Badge>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-5 text-center">
            <Award className="mx-auto h-5 w-5 text-yellow-500" />
            <p className="mt-2 text-3xl font-bold">{score.total_score}</p>
            <p className="text-xs text-muted-foreground">Total Score</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5 text-center">
            <TrendingUp className="mx-auto h-5 w-5 text-primary" />
            <p className="mt-2 text-3xl font-bold">Lv.{score.level}</p>
            <p className="text-xs text-muted-foreground">Level</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5 text-center">
            <Flame className="mx-auto h-5 w-5 text-orange-500" />
            <p className="mt-2 text-3xl font-bold">🔥 {score.current_streak}</p>
            <p className="text-xs text-muted-foreground">Current Streak</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5 text-center">
            <Trophy className="mx-auto h-5 w-5 text-purple-500" />
            <p className="mt-2 text-3xl font-bold">{score.longest_streak}</p>
            <p className="text-xs text-muted-foreground">Longest Streak</p>
          </CardContent>
        </Card>
      </div>

      {/* Level Progress */}
      <Card>
        <CardContent className="p-5">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Progress to Level {score.level + 1}</span>
            <span className="text-sm text-muted-foreground">
              {score.experience_points} / {score.next_level_xp} XP
            </span>
          </div>
          <Progress value={levelProgress} className="mt-2 h-2.5" />
        </CardContent>
      </Card>

      {/* Score Breakdown */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              <Star className="mr-1 inline h-4 w-4" /> Consistency
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{score.consistency_score}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              <BarChart3 className="mr-1 inline h-4 w-4" /> Engagement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{score.engagement_score}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              <Trophy className="mr-1 inline h-4 w-4" /> Milestones
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{score.milestone_score}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              <TrendingUp className="mr-1 inline h-4 w-4" /> Influence
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{score.influence_score}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Activity</CardTitle>
          <Dialog open={historyDialogOpen} onOpenChange={handleDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="ghost" size="sm" className="gap-1">
                View all <ChevronRight className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
              <DialogHeader>
                <DialogTitle>Score History</DialogTitle>
              </DialogHeader>

              <div className="flex-1 overflow-y-auto space-y-2 pr-2">
                {historyLoading && fullHistory.length === 0 ? (
                  <div className="flex justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                  </div>
                ) : fullHistory.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">No score history yet.</p>
                ) : (
                  fullHistory.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between rounded-lg border p-3 text-sm"
                    >
                      <div>
                        <p className="font-medium">{item.reason_label}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                        </p>
                      </div>
                      <span
                        className={`font-semibold ${
                          item.delta > 0 ? "text-green-600" : "text-red-600"
                        }`}
                      >
                        {item.delta > 0 ? "+" : ""}
                        {item.delta}
                      </span>
                    </div>
                  ))
                )}

                {historyHasMore && (
                  <div className="flex justify-center pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={loadMoreHistory}
                      disabled={historyLoading}
                    >
                      {historyLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                      Load more
                    </Button>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent className="space-y-2">
          {history.length === 0 ? (
            <p className="text-sm text-muted-foreground">No recent activity.</p>
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between rounded-lg border p-3 text-sm"
              >
                <div>
                  <p className="font-medium">{item.reason_label}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                  </p>
                </div>
                <span
                  className={`font-semibold ${item.delta > 0 ? "text-green-600" : "text-red-600"}`}
                >
                  {item.delta > 0 ? "+" : ""}
                  {item.delta}
                </span>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
