import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { authService, scoreService } from "@/services/auth";
import { toast } from "sonner";
import {
  Loader2,
  MapPin,
  Globe,
  UserPlus,
  UserCheck,
  FolderTree,
  ArrowRight,
  Calendar,
  Sparkles,
  User,
  Mail,
  CheckCircle,
  XCircle,
  Clock,
  Link2,
  Briefcase,
  Flag,
  Award,
  TrendingUp,
} from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ReportDialog } from "@/components/shared/ReportDialog";

export default function PublicProfile() {
  const { username } = useParams();
  const { user: currentUser } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [journeys, setJourneys] = useState([]);
  const [isFollowing, setIsFollowing] = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  const [notFound, setNotFound] = useState(false);
  const [score, setScore] = useState(null);
  const [scoreLoading, setScoreLoading] = useState(true);

  const isOwnProfile = currentUser?.username === username;

  useEffect(() => {
    const fetchProfileData = async () => {
      setLoading(true);
      setNotFound(false);
      try {
        const [profileRes, journeysRes, scoreRes] = await Promise.all([
          authService.getPublicProfile(username),
          authService.getUserJourneys(username),
          scoreService.getPublicScore(username).catch(() => null),
        ]);

        const profileData = profileRes.data;
        setProfile(profileData);
        setIsFollowing(profileData.is_following || false);

        setJourneys(journeysRes.data?.results || []);
        setScore(scoreRes?.data || null);
      } catch (err) {
        if (err.response?.status === 404) {
          setNotFound(true);
        } else {
          toast.error("Failed to load profile");
        }
      } finally {
        setLoading(false);
        setScoreLoading(false);
      }
    };

    if (username) {
      fetchProfileData();
    }
  }, [username]);

  const handleFollowToggle = async () => {
    if (isOwnProfile) return;
    setFollowLoading(true);
    try {
      if (isFollowing) {
        await authService.unfollow(profile.id);
        setIsFollowing(false);
        setProfile((prev) => ({
          ...prev,
          profile: {
            ...prev.profile,
            follower_count: Math.max((prev.profile?.follower_count || 0) - 1, 0),
          },
        }));
        toast.success("Unfollowed");
      } else {
        await authService.follow(profile.id);
        setIsFollowing(true);
        setProfile((prev) => ({
          ...prev,
          profile: {
            ...prev.profile,
            follower_count: (prev.profile?.follower_count || 0) + 1,
          },
        }));
        toast.success("Followed");
      }
    } catch (err) {
      toast.error(err.response?.data?.message || "Action failed");
    } finally {
      setFollowLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (notFound || !profile) {
    return (
      <div className="py-16 text-center">
        <p className="text-lg font-medium">User not found</p>
        <p className="text-sm text-muted-foreground">The user you're looking for doesn't exist.</p>
      </div>
    );
  }

  const initials = profile.username?.charAt(0)?.toUpperCase() || "U";

  const aboutItems = [
    {
      label: "Username",
      value: `@${profile.username}`,
      icon: <User className="h-4 w-4" />,
    },
    {
      label: "Full Name",
      value: `${profile.first_name} ${profile.last_name}`,
      icon: <User className="h-4 w-4" />,
    },
    {
      label: "Email",
      value: profile.email,
      icon: <Mail className="h-4 w-4" />,
    },
    ...(profile.profile?.location
      ? [
          {
            label: "Location",
            value: profile.profile.location,
            icon: <MapPin className="h-4 w-4" />,
          },
        ]
      : []),
    ...(profile.profile?.website
      ? [
          {
            label: "Website",
            value: (
              <a
                href={profile.profile.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                {profile.profile.website.replace(/^https?:\/\//, "")}
              </a>
            ),
            icon: <Link2 className="h-4 w-4" />,
          },
        ]
      : []),
    ...(profile.profile?.what_i_do
      ? [
          {
            label: "What I do",
            value: profile.profile.what_i_do,
            icon: <Briefcase className="h-4 w-4" />,
          },
        ]
      : []),
    ...(profile.profile?.bio
      ? [
          {
            label: "Bio",
            value: profile.profile.bio,
            icon: <Sparkles className="h-4 w-4" />,
          },
        ]
      : []),
    {
      label: "Verified",
      value: profile.is_verified ? (
        <span className="flex items-center gap-1 text-green-600">
          <CheckCircle className="h-4 w-4" /> Yes
        </span>
      ) : (
        <span className="flex items-center gap-1 text-red-500">
          <XCircle className="h-4 w-4" /> No
        </span>
      ),
      icon: profile.is_verified ? (
        <CheckCircle className="h-4 w-4 text-green-600" />
      ) : (
        <XCircle className="h-4 w-4 text-red-500" />
      ),
    },
    {
      label: "Member Since",
      value: new Date(profile.created_at).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
      }),
      icon: <Clock className="h-4 w-4" />,
    },
  ];

  const scoreItems = score
    ? [
        {
          label: "Total Score",
          value: score.total_score || 0,
          icon: <Award className="h-4 w-4 text-yellow-500" />,
        },
        {
          label: "Level",
          value: `Lv. ${score.level || 1}`,
          icon: <TrendingUp className="h-4 w-4 text-primary" />,
        },
        {
          label: "Current Streak",
          value: `🔥 ${score.current_streak || 0} days`,
          icon: <Sparkles className="h-4 w-4 text-orange-500" />,
        },
        {
          label: "Longest Streak",
          value: `🏆 ${score.longest_streak || 0} days`,
          icon: <Award className="h-4 w-4 text-purple-500" />,
        },
      ]
    : [];

  return (
    <div className="mx-auto max-w-4xl space-y-8 px-4 py-8 lg:px-0">
      <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start sm:gap-8">
        <Avatar className="h-28 w-28 border-4 border-primary/10 shadow-md sm:h-32 sm:w-32">
          <AvatarImage src={profile.profile?.avatar_url} alt={profile.username} />
          <AvatarFallback className="text-4xl">{initials}</AvatarFallback>
        </Avatar>

        <div className="flex-1 space-y-3 text-center sm:text-left">
          <div className="flex flex-wrap items-center justify-center gap-4 sm:justify-start">
            <h1 className="text-2xl font-bold tracking-tight">{profile.username}</h1>
            {profile.is_verified && (
              <Badge className="bg-green-600 px-2.5 py-0 text-xs font-medium">✓ Verified</Badge>
            )}
            {!isOwnProfile && (
              <Button
                variant={isFollowing ? "outline" : "default"}
                size="sm"
                onClick={handleFollowToggle}
                disabled={followLoading}
                className="shrink-0 cursor-pointer"
              >
                {followLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : isFollowing ? (
                  <>
                    <UserCheck className="mr-2 h-4 w-4" />
                    Following
                  </>
                ) : (
                  <>
                    <UserPlus className="mr-2 h-4 w-4" />
                    Follow
                  </>
                )}
              </Button>
            )}
            {!isOwnProfile && (
              <ReportDialog
                contentType="user"
                objectId={profile.id}
                trigger={
                  <Button variant="ghost" size="sm" className="gap-1.5">
                    <Flag className="h-4 w-4" />
                    Report
                  </Button>
                }
              />
            )}
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 sm:justify-start">
            <div>
              <span className="font-semibold">{profile.profile?.follower_count ?? 0}</span>
              <span className="ml-1 text-sm text-muted-foreground">Followers</span>
            </div>
            <div>
              <span className="font-semibold">{profile.profile?.following_count ?? 0}</span>
              <span className="ml-1 text-sm text-muted-foreground">Following</span>
            </div>
            <div>
              <span className="font-semibold">
                {profile.profile?.journey_count ?? journeys.length}
              </span>
              <span className="ml-1 text-sm text-muted-foreground">Journeys</span>
            </div>
          </div>

          <div className="space-y-1">
            <p className="text-sm font-medium">
              {profile.first_name} {profile.last_name}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-sm text-muted-foreground sm:justify-start">
              {profile.profile?.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="h-3.5 w-3.5" />
                  {profile.profile.location}
                </span>
              )}
              {profile.profile?.website && (
                <a
                  href={profile.profile.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-primary hover:underline"
                >
                  <Globe className="h-3.5 w-3.5" />
                  {profile.profile.website.replace(/^https?:\/\//, "")}
                </a>
              )}
            </div>
          </div>

          <div className="space-y-1 text-sm">
            {profile.profile?.bio && (
              <p className="leading-relaxed text-muted-foreground">{profile.profile.bio}</p>
            )}
            {profile.profile?.what_i_do && (
              <p className="flex items-center justify-center gap-1.5 text-muted-foreground sm:justify-start">
                <Sparkles className="h-4 w-4 text-yellow-500" />
                {profile.profile.what_i_do}
              </p>
            )}
          </div>
        </div>
      </div>

      <Tabs defaultValue="journeys" className="w-full">
        <TabsList className="grid w-full grid-cols-3 rounded-full bg-muted p-1 h-12">
          <TabsTrigger
            value="journeys"
            className="rounded-full text-sm font-medium transition-all
      data-[state=active]:bg-background
      data-[state=active]:text-foreground
      data-[state=active]:shadow-sm"
          >
            Journeys
          </TabsTrigger>
          <TabsTrigger
            value="score"
            className="rounded-full text-sm font-medium transition-all
      data-[state=active]:bg-background
      data-[state=active]:text-foreground
      data-[state=active]:shadow-sm"
          >
            Score
          </TabsTrigger>
          <TabsTrigger
            value="about"
            className="rounded-full text-sm font-medium transition-all
      data-[state=active]:bg-background
      data-[state=active]:text-foreground
      data-[state=active]:shadow-sm"
          >
            About
          </TabsTrigger>
        </TabsList>

        <TabsContent value="journeys" className="space-y-5 pt-6">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {journeys.length} journey{journeys.length !== 1 ? "s" : ""}
            </p>
          </div>

          {journeys.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed py-16">
              <FolderTree className="mb-4 h-12 w-12 text-muted-foreground/40" />
              <p className="text-lg font-medium">No journeys yet</p>
              <p className="text-sm text-muted-foreground">
                {profile.username} hasn't created any journeys yet.
              </p>
            </div>
          ) : (
            <div className="grid gap-5 sm:grid-cols-2">
              {journeys.map((journey) => (
                <Link
                  key={journey.id}
                  to={`/journeys/${journey.id}`}
                  className="group relative overflow-hidden rounded-xl border bg-card transition-all hover:border-primary/30 hover:shadow-md"
                >
                  <div className="p-5">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="truncate font-semibold group-hover:text-primary">
                          {journey.title}
                        </h3>
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          <Badge variant="outline" className="rounded-full text-xs font-normal">
                            {journey.category}
                          </Badge>
                          <Badge variant="secondary" className="rounded-full text-xs font-normal">
                            {journey.status}
                          </Badge>
                        </div>
                      </div>
                      <ArrowRight className="ml-3 h-4 w-4 shrink-0 text-muted-foreground/50 transition group-hover:translate-x-1 group-hover:text-primary" />
                    </div>

                    <div className="mt-4">
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="font-medium">{journey.latest_progress ?? 0}%</span>
                      </div>
                      <Progress value={journey.latest_progress ?? 0} className="mt-1.5 h-1.5" />
                    </div>

                    <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{journey.update_count} updates</span>
                      <span>·</span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(journey.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="score" className="pt-6">
          {scoreLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : score ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {scoreItems.map((item, idx) => (
                <Card key={idx} className="border bg-card transition-colors hover:bg-muted/30">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 rounded-md bg-primary/10 p-2 text-primary">
                        {item.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                          {item.label}
                        </p>
                        <p className="mt-1 text-xl font-bold">{item.value}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <Award className="mx-auto h-12 w-12 opacity-20" />
              <p className="mt-2">No score data available</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="about" className="pt-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {aboutItems.map((item, idx) => (
              <Card key={idx} className="border bg-card transition-colors hover:bg-muted/30">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 rounded-md bg-primary/10 p-2 text-primary">
                      {item.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                        {item.label}
                      </p>
                      <p className="mt-1 truncate text-sm font-medium">{item.value}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
