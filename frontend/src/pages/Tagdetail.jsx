import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { toast } from "sonner";
import { Loader2, Hash, ArrowLeft, Calendar, ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { journeyService } from "@/services/auth";

export default function TagDetail() {
  const { slug } = useParams();
  const [loading, setLoading] = useState(true);
  const [tag, setTag] = useState(null);
  const [journeys] = useState([]);

  useEffect(() => {
    const fetchTagData = async () => {
      setLoading(true);
      try {
        const [tagRes] = await Promise.all([journeyService.getTagDetail(slug)]);
        setTag(tagRes.data);
        // eslint-disable-next-line no-unused-vars
      } catch (err) {
        toast.error("Failed to load tag details");
      } finally {
        setLoading(false);
      }
    };
    if (slug) {
      fetchTagData();
    }
  }, [slug]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!tag) {
    return (
      <div className="py-12 text-center">
        <p className="text-muted-foreground">Tag not found.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/explore/trending-tags">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-primary/10 p-2 text-primary">
            <Hash className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">#{tag.name}</h1>
            <p className="text-sm text-muted-foreground">
              {tag.usage_count} {tag.usage_count === 1 ? "journey" : "journeys"} using this tag
            </p>
          </div>
        </div>
      </div>

      {journeys.length === 0 ? (
        <div className="py-12 text-center text-muted-foreground">
          {/* <p>No journeys with this tag yet.</p> */}
          <p>Journey Updates with this tags will appear here,in future.</p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2">
          {journeys.map((journey) => (
            <JourneyCard key={journey.id} journey={journey} />
          ))}
        </div>
      )}
    </div>
  );
}

function JourneyCard({ journey }) {
  const initials = journey.owner?.username?.charAt(0)?.toUpperCase() || "U";

  return (
    <Link
      to={`/journeys/${journey.id}`}
      className="group relative overflow-hidden rounded-xl border bg-card transition-all hover:border-primary/30 hover:shadow-md"
    >
      <div className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <Avatar className="h-6 w-6">
                <AvatarImage src={journey.owner?.avatar_url} alt={journey.owner?.username} />
                <AvatarFallback className="text-xs">{initials}</AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium text-muted-foreground">
                {journey.owner?.username}
              </span>
            </div>

            <h3 className="mt-2 truncate font-semibold group-hover:text-primary">
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
  );
}
