import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { journeyService } from "@/services/auth";
import { toast } from "sonner";
import { Loader2, Plus, FolderTree, ArrowRight, Calendar, Search, X } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { JourneysSkeleton } from "@/components/journey/JourneySkelton";

const STATUS_COLORS = {
  ACTIVE: "bg-green-500/10 text-green-600 border-green-500/20",
  PAUSED: "bg-yellow-500/10 text-yellow-600 border-yellow-500/20",
  COMPLETED: "bg-blue-500/10 text-blue-600 border-blue-500/20",
  ABANDONED: "bg-red-500/10 text-red-600 border-red-500/20",
};

const CATEGORY_LABELS = {
  SOFTWARE: "Software",
  STARTUP: "Startup",
  SKILL: "Skill",
  RESEARCH: "Research",
  BOOK: "Book",
  ART: "Art",
  FITNESS: "Fitness",
  DIY: "DIY",
  CONTENT: "Content",
  CHALLENGE: "Challenge",
  OTHER: "Other",
};

export default function Journeys() {
  const [loading, setLoading] = useState(true);
  const [journeys, setJourneys] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const pageSize = 12;

  const fetchJourneys = async (pageNum = 1, reset = false) => {
    setLoading(true);
    try {
      const params = {
        page: pageNum,
        page_size: pageSize,
        search: searchQuery || undefined,
        status: statusFilter || undefined,
        category: categoryFilter || undefined,
      };
      const response = await journeyService.getJourneys(params);
      const data = response.data;
      const results = data.results || [];

      if (reset || pageNum === 1) {
        setJourneys(results);
      } else {
        setJourneys((prev) => [...prev, ...results]);
      }

      setTotalCount(data.count || 0);
      setHasNext(!!data.next);
      setPage(pageNum);
      // eslint-disable-next-line no-unused-vars
    } catch (err) {
      toast.error("Failed to load journeys");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchJourneys(1, true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, categoryFilter]);

  const loadMore = () => {
    if (!hasNext || loading) return;
    fetchJourneys(page + 1);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchJourneys(1, true);
  };

  const clearFilters = () => {
    setSearchQuery("");
    setStatusFilter("");
    setCategoryFilter("");
    fetchJourneys(1, true);
  };

  if (loading && journeys.length === 0) {
    return <JourneysSkeleton />;
  }

  return (
    <div className="mx-auto max-w-6xl px-15 py-10">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <FolderTree className="h-6 w-6 text-primary" />
            All Journeys
          </h1>
          <p className="text-sm text-muted-foreground">
            {totalCount} journey{totalCount !== 1 ? "s" : ""} found
          </p>
        </div>
        <Button>
          <Link to="/journeys/create" className="inline-flex items-center gap-2">
            <Plus className="h-4 w-4" />
            <span>New Journey</span>
          </Link>
        </Button>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center mb-6">
        <form onSubmit={handleSearchSubmit} className="flex-1 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search journeys..."
              className="pl-9 pr-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery("");
                  fetchJourneys(1, true);
                }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          <Button type="submit" variant="secondary" size="lg" className="shrink-0">
            Search
          </Button>
        </form>

        <div className="flex flex-wrap gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-32.5">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All</SelectItem>
              <SelectItem value="ACTIVE">Active</SelectItem>
              <SelectItem value="PAUSED">Paused</SelectItem>
              <SelectItem value="COMPLETED">Completed</SelectItem>
              <SelectItem value="ABANDONED">Abandoned</SelectItem>
            </SelectContent>
          </Select>

          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger className="w-32.5">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All</SelectItem>
              {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
                <SelectItem key={key} value={key}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {(statusFilter || categoryFilter) && (
            <Button variant="ghost" size="sm" onClick={clearFilters} className="shrink-0 gap-1">
              <X className="h-3 w-3" />
              Clear
            </Button>
          )}
        </div>
      </div>

      {journeys.length === 0 && !loading ? (
        <Card className="border-dashed">
          <CardContent className="py-16 text-center">
            <FolderTree className="mx-auto h-12 w-12 text-muted-foreground/40" />
            <p className="mt-4 text-lg font-medium text-muted-foreground">No journeys found</p>
            <p className="text-sm text-muted-foreground">
              {searchQuery || statusFilter || categoryFilter
                ? "Try adjusting your filters"
                : "Be the first to share your journey!"}
            </p>
            {!searchQuery && !statusFilter && !categoryFilter && (
              <Button asChild className="mt-4 gap-1.5">
                <Link
                  to="/journeys/create"
                  className="inline-flex items-center gap-2 whitespace-nowrap"
                >
                  <Plus className="h-4 w-4" />
                  Create Journey
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {journeys.map((journey) => (
              <Link key={journey.id} to={`/journeys/${journey.id}`} className="group block">
                <Card className="h-full overflow-hidden rounded-xl border bg-card transition-all hover:shadow-md hover:border-primary/30">
                  <CardContent className="p-5 flex flex-col h-full">
                    <div className="flex-1">
                      <div className="flex items-start justify-between gap-2">
                        <h3 className="font-semibold line-clamp-1 group-hover:text-primary transition-colors">
                          {journey.title}
                        </h3>
                        <Badge
                          variant="outline"
                          className={`text-xs shrink-0 ${STATUS_COLORS[journey.status] || ""}`}
                        >
                          {journey.status}
                        </Badge>
                      </div>

                      <div className="mt-2 flex flex-wrap gap-1.5">
                        <Badge variant="secondary" className="text-xs rounded-full">
                          {CATEGORY_LABELS[journey.category] || journey.category}
                        </Badge>
                        <Badge variant="outline" className="text-xs rounded-full">
                          {journey.visibility}
                        </Badge>
                      </div>

                      {/* Owner */}
                      <div className="mt-3 flex items-center gap-2">
                        <Avatar className="h-5 w-5">
                          <AvatarImage
                            src={journey.owner?.avatar_url}
                            alt={journey.owner?.username}
                          />
                          <AvatarFallback className="text-[10px]">
                            {journey.owner?.username?.charAt(0)?.toUpperCase() || "U"}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-xs text-muted-foreground hover:underline">
                          {journey.owner?.username}
                        </span>
                      </div>

                      <div className="mt-4">
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Progress</span>
                          <span className="font-medium">{journey.latest_progress || 0}%</span>
                        </div>
                        <Progress value={journey.latest_progress || 0} className="mt-1.5 h-1.5" />
                      </div>
                    </div>

                    <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground border-t pt-3">
                      <div className="flex items-center gap-3">
                        <span>{journey.update_count} updates</span>
                        <span className="w-1 h-1 rounded-full bg-muted-foreground/30" />
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDistanceToNow(new Date(journey.created_at), {
                            addSuffix: true,
                          })}
                        </span>
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground/50 group-hover:translate-x-0.5 transition group-hover:text-primary" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          {hasNext && (
            <div className="flex justify-center pt-6">
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
        </>
      )}
    </div>
  );
}
