import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { Loader2, Hash, TrendingUp, ArrowRight } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { journeyService } from "@/services/auth";

export default function ExploreTags() {
  const [loading, setLoading] = useState(true);
  const [tags, setTags] = useState([]);

  useEffect(() => {
    const fetchTrendingTags = async () => {
      setLoading(true);
      try {
        const response = await journeyService.getTrendingTags();
        setTags(response.data || []);
      // eslint-disable-next-line no-unused-vars
      } catch (err) {
        toast.error("Failed to load trending tags");
      } finally {
        setLoading(false);
      }
    };
    fetchTrendingTags();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (tags.length === 0) {
    return (
      <div className="py-12 text-center text-muted-foreground">
        <TrendingUp className="mx-auto h-12 w-12 opacity-20" />
        <p className="mt-4">No trending tags yet</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8">
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-primary/10 p-2 text-primary">
          <TrendingUp className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Trending Tags</h1>
          <p className="text-sm text-muted-foreground">Most popular tags used in journeys</p>
        </div>
        <Badge variant="secondary" className="ml-auto">
          {tags.length} tags
        </Badge>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {tags.map((tag) => (
          <Link key={tag.id} to={`/explore/tags/${tag.slug}`} className="group block">
            <Card className="overflow-hidden rounded-xl border bg-card transition-all hover:border-primary/30 hover:shadow-md">
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                      <Hash className="h-4 w-4" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="truncate font-semibold group-hover:text-primary transition-colors">
                        #{tag.name}
                      </h3>
                      <p className="text-xs text-muted-foreground">
                        {tag.usage_count} {tag.usage_count === 1 ? "use" : "uses"}
                      </p>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground/50 transition group-hover:translate-x-1 group-hover:text-primary" />
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
