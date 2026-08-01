import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authService } from "@/services/auth";
import { toast } from "sonner";
import {
  Loader2,
  MapPin,
  Globe,
  ArrowRight,
  Plus,
  FolderTree,
  Award,
  Calendar,
  Sparkles,
  User,
  Mail,
  CheckCircle,
  XCircle,
  Clock,
  Link2,
  Briefcase,
} from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";

export default function Profile() {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [journeys, setJourneys] = useState([]);
  const [score, setScore] = useState(null);

  useEffect(() => {
    const fetchProfileData = async () => {
      setLoading(true);

      try {
        const [profileRes, journeysRes, scoreRes] = await Promise.all([
          authService.getProfile(),
          authService.getJourneys(),
          authService.getScore(),
        ]);

        const profileData = profileRes.data;
        const journeysData = journeysRes.data?.results ?? [];
        const scoreData = scoreRes.data;

        setProfile(profileData);
        setJourneys(journeysData);
        setScore(scoreData);
      } catch (err) {
        console.error(err);
        toast.error("Failed to load profile data");
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="py-16 text-center">
        <p className="text-muted-foreground">Unable to load profile.</p>
      </div>
    );
  }

  const initials = (
    profile.first_name?.charAt(0) ||
    profile.username?.charAt(0) ||
    "U"
  ).toUpperCase();

  const progress =
    score && score.next_level_xp ? (score.experience_points / score.next_level_xp) * 100 : 0;

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
            <div>
              <span className="font-semibold text-yellow-600">{score?.total_score ?? 0}</span>
              <span className="ml-1 text-sm text-muted-foreground">Score</span>
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
            Builder Score
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
            <Button asChild className="rounded-full">
              <Link to="/journeys/create" className="inline-flex items-center gap-2">
                <Plus className="size-4" />
                New Journey
              </Link>
            </Button>
          </div>

          {journeys.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed py-16">
              <FolderTree className="mb-4 h-12 w-12 text-muted-foreground/40" />
              <p className="text-lg font-medium">No journeys yet</p>
              <p className="text-sm text-muted-foreground">Start documenting your first journey</p>
              <Button asChild className="mt-5">
                <Link to="/journeys/create">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Journey
                </Link>
              </Button>
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

          {journeys.length > 0 && (
            <div className="text-center">
              <Button asChild variant="link" className="text-sm">
                <Link to="/journeys">
                  View all journeys
                  <ArrowRight className="ml-1 inline h-4 w-4" />
                </Link>
              </Button>
            </div>
          )}
        </TabsContent>

        <TabsContent value="score" className="space-y-0 pt-6">
          {score ? (
            <>
              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Score</p>
                      <p className="text-4xl font-bold tracking-tight">{score.total_score}</p>
                    </div>
                    <div className="flex items-center gap-6">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Level</p>
                        <p className="text-3xl font-bold text-primary">Lv.{score.level}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Streak</p>
                        <p className="text-2xl font-bold">🔥 {score.current_streak}</p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-5">
                    <div className="flex justify-between text-sm">
                      <span>{score.experience_points} XP</span>
                      <span className="text-muted-foreground">
                        {score.next_level_xp} XP to next level
                      </span>
                    </div>
                    <Progress value={progress} className="mt-1.5 h-2" />
                  </div>

                  <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
                    <div className="rounded-lg bg-muted/50 p-3 text-center">
                      <p className="text-sm text-muted-foreground">Consistency</p>
                      <p className="text-xl font-bold">{score.consistency_score}</p>
                    </div>
                    <div className="rounded-lg bg-muted/50 p-3 text-center">
                      <p className="text-sm text-muted-foreground">Milestones</p>
                      <p className="text-xl font-bold">{score.milestone_score}</p>
                    </div>
                    <div className="rounded-lg bg-muted/50 p-3 text-center">
                      <p className="text-sm text-muted-foreground">Engagement</p>
                      <p className="text-xl font-bold">{score.engagement_score}</p>
                    </div>
                    <div className="rounded-lg bg-muted/50 p-3 text-center">
                      <p className="text-sm text-muted-foreground">Influence</p>
                      <p className="text-xl font-bold">{score.influence_score}</p>
                    </div>
                  </div>

                  {score.longest_streak > 0 && (
                    <p className="mt-4 text-sm text-muted-foreground">
                      Longest streak: {score.longest_streak} days
                    </p>
                  )}
                </CardContent>
              </Card>

              <Button asChild variant="outline" className="w-full">
                <Link to="/score/history">View full score history</Link>
              </Button>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed py-16">
              <Award className="mb-4 h-12 w-12 text-muted-foreground/40" />
              <p className="text-lg font-medium">No score data</p>
              <p className="text-sm text-muted-foreground">
                Start building and engaging to earn points
              </p>
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
