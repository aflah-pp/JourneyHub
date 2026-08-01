import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { dashboardService } from "@/services/dashboard";
import { toast } from "sonner";
import {
  Loader2,
  FolderTree,
  FileText,
  Heart,
  Plus,
  ArrowRight,
  User,
  Award,
  TrendingUp,
  Activity,
  CheckCircle,
  AlertCircle,
  Flame,
  Trophy,
} from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { formatDistanceToNow } from "date-fns";

export default function Dashboard() {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [score, setScore] = useState(null);
  const [journeys, setJourneys] = useState([]);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await dashboardService.getDashboardData();
        setScore(data.score);
        setJourneys(data.journeys);
        setHistory(data.history.slice(0, 5));
      // eslint-disable-next-line no-unused-vars
      } catch (err) {
        toast.error("Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const username = user?.username || "User";
  const initials =
    user?.username
      ?.split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase() || "U";

  const totalJourneys = journeys.length;
  const totalUpdates = journeys.reduce((acc, j) => acc + (j.update_count || 0), 0);
  const totalLikes = score?.engagement_score || 0;

  return (
    <div className="space-y-6 p-7">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <User className="h-6 w-6 text-primary" />
          Welcome back, {username}!
        </h1>
        <p className="text-muted-foreground">Here's what's happening with your journeys</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <User className="h-4 w-4" /> Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={user?.profile?.avatar_url} alt={user?.username} />
              <AvatarFallback className="text-lg">{initials}</AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold">@{user?.username || "USER"}</p>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
              {user?.is_verified ? (
                <Badge
                  variant="default"
                  className="mt-1 text-xs bg-green-500 hover:bg-green-600 flex items-center gap-1"
                >
                  <CheckCircle className="h-3 w-3" /> Verified
                </Badge>
              ) : (
                <Badge
                  variant="outline"
                  className="mt-1 text-xs text-yellow-600 border-yellow-600 flex items-center gap-1"
                >
                  <AlertCircle className="h-3 w-3" /> Verify Email
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <Award className="h-4 w-4" /> Builder Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            {score ? (
              <>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold">{score.total_score}</p>
                    <p className="text-sm text-muted-foreground">Total Points</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary">Lv.{score.level}</p>
                    <p className="text-sm text-muted-foreground">Level</p>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-muted-foreground mb-1">
                    <span>{score.experience_points} XP</span>
                    <span>{score.next_level_xp} XP</span>
                  </div>
                  <Progress
                    value={(score.experience_points / score.next_level_xp) * 100}
                    className="h-2"
                  />
                </div>
                <div className="mt-3 flex justify-between text-xs">
                  <span className="flex items-center gap-1">
                    <Flame className="h-3.5 w-3.5" /> {score.current_streak} day streak
                  </span>
                  <span className="flex items-center gap-1">
                    <Trophy className="h-3.5 w-3.5" /> {score.longest_streak} longest
                  </span>
                </div>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">No score data</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <Activity className="h-4 w-4" /> Activity Stats
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-2">
              <div className="text-center">
                <FolderTree className="h-5 w-5 mx-auto text-muted-foreground" />
                <p className="text-xl font-bold mt-1">{totalJourneys}</p>
                <p className="text-xs text-muted-foreground">Journeys</p>
              </div>
              <div className="text-center">
                <FileText className="h-5 w-5 mx-auto text-muted-foreground" />
                <p className="text-xl font-bold mt-1">{totalUpdates}</p>
                <p className="text-xs text-muted-foreground">Updates</p>
              </div>
              <div className="text-center">
                <Heart className="h-5 w-5 mx-auto text-muted-foreground" />
                <p className="text-xl font-bold mt-1">{totalLikes}</p>
                <p className="text-xs text-muted-foreground">Likes</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Journeys */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <FolderTree className="h-4 w-4" /> Recent Journeys
            </CardTitle>
            <Link to="/journeys">
              <Button variant="ghost" size="sm" className="text-xs">
                View All <ArrowRight className="ml-1 h-3 w-3" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {journeys.length > 0 ? (
              <div className="space-y-3 max-h-48 overflow-y-auto pr-1">
                {journeys.slice(0, 3).map((journey) => (
                  <div
                    key={journey.id}
                    className="border rounded-lg p-3 hover:bg-muted/50 transition-colors"
                  >
                    <Link to={`/journeys/${journey.id}`} className="block">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-sm hover:underline">{journey.title}</p>
                          <p className="text-xs text-muted-foreground">
                            {journey.category} • {journey.update_count} updates
                          </p>
                        </div>
                        <span className="text-sm font-medium">{journey.latest_progress || 0}%</span>
                      </div>
                      <Progress value={journey.latest_progress || 0} className="h-1.5 mt-2" />
                    </Link>
                  </div>
                ))}
                {journeys.length > 3 && (
                  <div className="text-center text-xs text-muted-foreground">
                    +{journeys.length - 3} more
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <p className="text-sm">No journeys yet</p>
                <Link to="/journeys/create">
                  <Button variant="outline" size="sm" className="mt-2">
                    <Plus className="mr-1 h-4 w-4" />
                    Create your first journey
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          {/* Recent Score Changes */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                <TrendingUp className="h-4 w-4" /> Recent Score Changes
              </CardTitle>
              <Link to="/score/history">
                <Button variant="ghost" size="sm" className="text-xs">
                  View All <ArrowRight className="ml-1 h-3 w-3" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {history.length > 0 ? (
                <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                  {history.slice(0, 4).map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between text-sm border-b pb-2 last:border-0 last:pb-0"
                    >
                      <div>
                        <p className="font-medium">{item.reason_label}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(item.created_at), {
                            addSuffix: true,
                          })}
                        </p>
                      </div>
                      <span
                        className={
                          item.delta > 0
                            ? "text-green-600 font-semibold"
                            : "text-red-600 font-semibold"
                        }
                      >
                        {item.delta > 0 ? "+" : ""}
                        {item.delta}
                      </span>
                    </div>
                  ))}
                  {history.length > 4 && (
                    <div className="text-center text-xs text-muted-foreground">
                      +{history.length - 4} more
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No score history yet
                </p>
              )}
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                <Activity className="h-4 w-4" /> Recent Activity
              </CardTitle>
              <Link to="/activity">
                <Button variant="ghost" size="sm" className="text-xs">
                  View All <ArrowRight className="ml-1 h-3 w-3" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                {[
                  { action: "Created new journey", time: "2 hours ago" },
                  { action: "Posted an update", time: "5 hours ago" },
                  { action: "Received 3 likes", time: "1 day ago" },
                  { action: "Completed milestone", time: "2 days ago" },
                ]
                  .slice(0, 4)
                  .map((activity, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between text-sm border-b pb-2 last:border-0 last:pb-0"
                    >
                      <span>{activity.action}</span>
                      <span className="text-xs text-muted-foreground">{activity.time}</span>
                    </div>
                  ))}
                {[
                  { action: "Created new journey", time: "2 hours ago" },
                  { action: "Posted an update", time: "5 hours ago" },
                  { action: "Received 3 likes", time: "1 day ago" },
                  { action: "Completed milestone", time: "2 days ago" },
                ].length > 4 && (
                  <div className="text-center text-xs text-muted-foreground">+1 more</div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
