import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { journeyService, reactionService } from "@/services/auth";
import { toast } from "sonner";
import {
  ArrowLeft,
  Edit,
  Trash2,
  Plus,
  Bookmark,
  BookmarkCheck,
  Share2,
  Flag,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { FolderTree } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useAuthStore } from "@/store/authStore";
import { JourneyInfoPanel } from "@/components/journey/JourneyInfoPanel";
import { UpdateList } from "@/components/journey/UpdateList";
import { JourneyDetailSkeleton } from "@/components/journey/JourneyDetailSkelton";
import { ReportDialog } from "@/components/shared/ReportDialog";

const actionBtn = "h-10 rounded-xl px-4 gap-2 font-medium transition-all duration-200";

export default function JourneyDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [journey, setJourney] = useState(null);
  const [updates, setUpdates] = useState([]);
  const [updatesLoading, setUpdatesLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [totalUpdates, setTotalUpdates] = useState(0);
  const [sort, setSort] = useState("newest");
  const [isSaved, setIsSaved] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const pageSize = 10;

  const isOwner = currentUser?.id === journey?.owner?.id;

  const fetchJourney = async () => {
    try {
      const response = await journeyService.getJourneyDetail(id);
      let journeyData = response.data;
      if (
        journeyData &&
        typeof journeyData === "object" &&
        journeyData.results &&
        Array.isArray(journeyData.results) &&
        journeyData.results.length > 0
      ) {
        journeyData = journeyData.results[0];
      }
      setJourney(journeyData);
      if (journeyData && typeof journeyData.is_saved_by_me !== "undefined") {
        setIsSaved(journeyData.is_saved_by_me);
      } else {
        setIsSaved(false);
      }
    } catch {
      toast.error("Failed to load journey");
      navigate("/journeys");
    }
  };

  const fetchUpdates = async (pageNum = 1) => {
    setUpdatesLoading(true);
    try {
      const params = { page: pageNum, page_size: pageSize };
      if (sort === "oldest") params.ordering = "created_at";
      else if (sort === "most_liked") params.ordering = "-like_count";
      else params.ordering = "-created_at";

      const response = await journeyService.getJourneyUpdates(id, params);
      const data = response.data;
      const results = data.results || [];

      if (pageNum === 1) {
        setUpdates(results);
      } else {
        setUpdates((prev) => [...prev, ...results]);
      }

      setTotalUpdates(data.count || 0);
      setHasNext(!!data.next);
      setPage(pageNum);
    } catch {
      toast.error("Failed to load updates");
    } finally {
      setUpdatesLoading(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await fetchJourney();
      await fetchUpdates(1);
      setLoading(false);
    };
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, sort]);

  const loadMoreUpdates = () => {
    if (!hasNext || updatesLoading) return;
    fetchUpdates(page + 1);
  };

  const handleDelete = async () => {
    try {
      await journeyService.deleteJourney(id);
      toast.success("Journey deleted successfully");
      navigate("/journeys");
    } catch {
      toast.error("Failed to delete journey");
    } finally {
      setDeleteDialogOpen(false);
    }
  };

  const toggleSave = async () => {
    if (!currentUser) {
      toast.error("Please login to save journeys");
      return;
    }
    setSaveLoading(true);
    try {
      if (isSaved) {
        await reactionService.unsaveJourney(id);
        setIsSaved(false);
        toast.success("Journey unsaved");
      } else {
        await reactionService.toggleSaveJourney(id);
        setIsSaved(true);
        toast.success("Journey saved");
      }
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to toggle save");
    } finally {
      setSaveLoading(false);
    }
  };

  if (loading) {
    return <JourneyDetailSkeleton />;
  }

  if (!journey) {
    return (
      <div className="flex items-center justify-center h-full">
        <Card>
          <CardContent className="py-16 text-center">
            <FolderTree className="mx-auto h-12 w-12 text-muted-foreground/40" />
            <p className="mt-4 text-lg font-medium text-muted-foreground">Journey not found</p>
            <Button asChild className="mt-4">
              <Link to="/journeys">Back to Journeys</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full min-h-0 overflow-hidden max-w-[1600px] mx-auto px-8 py-4 w-full">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4 shrink-0">
        <div className="flex min-w-0 items-center gap-3">
          <Button variant="ghost" size="icon" className="shrink-0" asChild>
            <Link to="/journeys">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>

          <h1 className="min-w-0 flex-1 truncate text-lg font-bold tracking-tight sm:text-xl md:text-2xl">
            {journey.title}
          </h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {isOwner ? (
            <>
              <Button
                variant={isSaved ? "secondary" : "outline"}
                size="sm"
                className={actionBtn}
                onClick={toggleSave}
                disabled={saveLoading}
              >
                {saveLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : isSaved ? (
                  <BookmarkCheck className="h-4 w-4 text-emerald-600" />
                ) : (
                  <Bookmark className="h-4 w-4" />
                )}
                <span>{isSaved ? "Saved" : "Save"}</span>
              </Button>

              <Button asChild size="sm" className={`${actionBtn} shadow-sm`}>
                <Link
                  to={`/journeys/${id}/updates/create`}
                  className="inline-flex items-center gap-2 whitespace-nowrap"
                >
                  <Plus className="h-4 w-4" />
                  New Update
                </Link>
              </Button>

              <Button asChild variant="secondary" size="sm" className={actionBtn}>
                <Link
                  to={`/journeys/${id}/edit`}
                  className="inline-flex items-center gap-2 whitespace-nowrap"
                >
                  <Edit className="h-4 w-4" />
                  Edit
                </Link>
              </Button>

              <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive" size="sm" className={actionBtn}>
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Delete Journey</AlertDialogTitle>
                    <AlertDialogDescription>
                      Are you sure you want to delete "{journey.title}"? This action cannot be
                      undone and all associated updates will be removed.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={handleDelete}
                      className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    >
                      Delete
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </>
          ) : (
            <>
              <Button
                variant={isSaved ? "secondary" : "outline"}
                size="sm"
                className={actionBtn}
                onClick={toggleSave}
                disabled={saveLoading}
              >
                {saveLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : isSaved ? (
                  <BookmarkCheck className="h-4 w-4 text-emerald-600" />
                ) : (
                  <Bookmark className="h-4 w-4" />
                )}
                {isSaved ? "Saved" : "Save"}
              </Button>

              <Button
                variant="ghost"
                size="sm"
                className={actionBtn}
                onClick={() => toast.info("Share feature coming soon")}
              >
                <Share2 className="h-4 w-4" />
                Share
              </Button>

              <ReportDialog
                contentType="journey"
                objectId={id}
                trigger={
                  <Button variant="ghost" size="sm" className="gap-1.5">
                    <Flag className="h-4 w-4" />
                    Report
                  </Button>
                }
              />
            </>
          )}
        </div>
      </div>

      {/* Main grid */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-[380px_1fr] h-full gap-8">
          <JourneyInfoPanel journey={journey} />
          <UpdateList
            updates={updates}
            totalUpdates={totalUpdates}
            updatesLoading={updatesLoading}
            hasNext={hasNext}
            loadMoreUpdates={loadMoreUpdates}
            sort={sort}
            setSort={setSort}
            journeyId={id}
            isOwner={isOwner}
          />
        </div>
      </div>
    </div>
  );
}
