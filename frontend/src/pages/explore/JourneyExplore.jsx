import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { Search, Loader2, FolderTree, ArrowRight, Calendar, X } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { journeyService } from "@/services/auth";

export default function ExploreJourneys() {
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const handleSearch = async (e) => {
    e.preventDefault();
    const trimmed = searchQuery.trim();
    if (!trimmed) {
      toast.warning("Please enter a search term");
      return;
    }

    setLoading(true);
    setSearchPerformed(true);
    try {
      const response = await journeyService.searchJourneys(trimmed);
      const data = response.data;
      setResults(data.results || []);
      setTotalCount(data.count || 0);
    } catch (err) {
      toast.error(err.response?.data?.message || "Search failed");
      setResults([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery("");
    setResults([]);
    setSearchPerformed(false);
    setTotalCount(0);
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Explore Journeys</h1>
        <p className="text-sm text-muted-foreground">Discover journeys from the community</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search journeys by title or description..."
            className="pl-9 pr-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <Button type="submit" disabled={loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Search"}
        </Button>
      </form>

      {searchPerformed ? (
        loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : results.length === 0 ? (
          <div className="py-12 text-center">
            <FolderTree className="mx-auto h-12 w-12 text-muted-foreground/40" />
            <p className="mt-4 text-muted-foreground">No journeys found.</p>
            <p className="text-sm text-muted-foreground">Try a different search term.</p>
          </div>
        ) : (
          <>
            <p className="text-sm text-muted-foreground">
              Found {totalCount} journey{totalCount !== 1 ? "s" : ""}
            </p>
            <div className="grid gap-5 sm:grid-cols-2">
              {results.map((journey) => (
                <JourneyCard key={journey.id} journey={journey} />
              ))}
            </div>
          </>
        )
      ) : (
        <div className="py-12 text-center text-muted-foreground">
          <Search className="mx-auto h-12 w-12 opacity-20" />
          <p className="mt-4">Search for journeys to get started</p>
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
              <Badge variant="outline" className="rounded-full text-xs font-normal">
                {journey.visibility}
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
