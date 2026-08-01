import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { FileText, Plus, ChevronDown, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";
import { UpdateCard } from "./UpdateCard";
import { UpdateSkeleton } from "./UpdateSkelton";

export function UpdateList({
  updates,
  totalUpdates,
  updatesLoading,
  hasNext,
  loadMoreUpdates,
  sort,
  setSort,
  journeyId,
  isOwner,
}) {
  return (
    <section className="h-full overflow-y-auto pr-2 pb-4 space-y-6 scrollbar-thin">
      {/* Sticky header */}
      <div className="flex flex-wrap items-center justify-between gap-3 sticky top-0 bg-background/95 backdrop-blur-sm z-10 py-2">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary" />
          Updates
          <span className="ml-1 text-sm font-normal text-muted-foreground">({totalUpdates})</span>
        </h2>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-1.5">
                {sort === "newest" && "Newest"}
                {sort === "oldest" && "Oldest"}
                {sort === "most_liked" && "Most Liked"}
                <ChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setSort("newest")}>Newest</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSort("oldest")}>Oldest</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSort("most_liked")}>Most Liked</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Content */}
      {updatesLoading && updates.length === 0 ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <UpdateSkeleton key={i} />
          ))}
        </div>
      ) : updates.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="py-16 text-center">
            <div className="text-4xl mb-4">🚀</div>
            <p className="text-lg font-medium text-muted-foreground">
              This journey has no updates yet.
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Create the first update and start documenting progress.
            </p>
            {isOwner && (
              <Button asChild className="mt-4">
                <Link
                  to={`/journeys/${journeyId}/updates/create`}
                  className="inline-flex items-center gap-2 whitespace-nowrap"
                >
                  <Plus className="h-4 w-4 shrink-0" />
                  <span>Create First Update</span>
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {updates.map((update) => (
            <UpdateCard key={update.id} update={update} journeyId={journeyId} />
          ))}
        </div>
      )}

      {hasNext && (
        <div className="flex justify-center pt-4 pb-2">
          <Button
            variant="outline"
            onClick={loadMoreUpdates}
            disabled={updatesLoading}
            className="w-full max-w-sm"
          >
            {updatesLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Loading...
              </>
            ) : (
              "Load more updates"
            )}
          </Button>
        </div>
      )}
    </section>
  );
}
