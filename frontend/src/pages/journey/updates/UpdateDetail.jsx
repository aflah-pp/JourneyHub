import { useEffect, useState, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { journeyService, reactionService } from "@/services/auth";
import { toast } from "sonner";
import {
  Loader2,
  ArrowLeft,
  Edit,
  Trash2,
  Heart,
  MessageCircle,
  Clock,
  Calendar,
  Plus,
  X,
  Bookmark,
  BookmarkCheck,
  CheckCircle,
  Flag,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { ReportDialog } from "@/components/shared/ReportDialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselPrevious,
  CarouselNext,
} from "@/components/ui/carousel";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
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
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuthStore } from "@/store/authStore";

import { useComments } from "@/hooks/useComments";
import { useTags } from "@/hooks/useTags";
import { CommentItem } from "@/components/reaction/CommentIndex";

const MILESTONE_LABELS = {
  NONE: "None",
  MILESTONE: "Milestone",
  COMPLETED: "Completed",
  IN_PROGRESS: "In Progress",
  FAILED: "Failed",
};

const MILESTONE_COLORS = {
  NONE: "bg-gray-100 text-gray-600",
  MILESTONE: "bg-violet-100 text-violet-700",
  COMPLETED: "bg-emerald-100 text-emerald-700",
  IN_PROGRESS: "bg-amber-100 text-amber-700",
  FAILED: "bg-rose-100 text-rose-700",
};

export default function UpdateDetail() {
  const { journeyId, updateId } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuthStore();

  const [loading, setLoading] = useState(true);
  const [update, setUpdate] = useState(null);
  const [acceptedSolution, setAcceptedSolution] = useState(null);
  const [likeCount, setLikeCount] = useState(0);
  const [isLiked, setIsLiked] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [liking, setLiking] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [images, setImages] = useState([]);
  const [commentsDialogOpen, setCommentsDialogOpen] = useState(false);

  const comments = useComments(updateId);
  const tags = useTags(journeyId, updateId, []);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [updateRes, solutionRes] = await Promise.all([
          journeyService.getUpdateDetail(journeyId, updateId),
          reactionService.getAcceptedSolution(updateId).catch(() => null),
        ]);

        const data = updateRes.data;
        setUpdate(data);
        setImages(data.images || []);
        setLikeCount(data.like_count || 0);
        setIsLiked(data.is_liked_by_me || false);
        setIsSaved(data.is_saved_by_me || false);
        tags.setTags(data.tags || []);
        if (solutionRes) {
          setAcceptedSolution(solutionRes.data);
        }
      } catch {
        toast.error("Failed to load update");
        navigate(`/journeys/${journeyId}`);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [journeyId, updateId]);

  const handleLike = useCallback(async () => {
    if (liking) return;
    setLiking(true);
    const newLiked = !isLiked;
    const newCount = newLiked ? likeCount + 1 : likeCount - 1;
    setIsLiked(newLiked);
    setLikeCount(newCount);
    try {
      if (newLiked) {
        await reactionService.toggleLike(updateId);
        toast.success("Journey update liked");
      } else {
        await reactionService.toggleUnLike(updateId);
        toast.success("Journey update  disliked");
      }
    } catch {
      setIsLiked(!newLiked);
      setLikeCount(likeCount);
      toast.error("Failed to update like");
    } finally {
      setLiking(false);
    }
  }, [isLiked, likeCount, liking, updateId]);

  const handleSave = useCallback(async () => {
    if (saving) return;
    setSaving(true);
    const newSaved = !isSaved;
    setIsSaved(newSaved);
    try {
      if (newSaved) {
        await reactionService.toggleSave(updateId);
        toast.success("Journey update saved");
      } else {
        await reactionService.unsaveUpdate(updateId);
        toast.success("Journey update  unsaved");
      }
    } catch {
      setIsSaved(!newSaved);
      toast.error("Failed to update save");
    } finally {
      setSaving(false);
    }
  }, [isSaved, saving, updateId]);

  const handleDelete = useCallback(async () => {
    setDeleting(true);
    try {
      await journeyService.deleteUpdate(journeyId, updateId);
      toast.success("Update deleted");
      navigate(`/journeys/${journeyId}`);
    } catch {
      toast.error("Failed to delete update");
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
    }
  }, [journeyId, updateId, navigate]);

  const handleAcceptSolution = useCallback(
    async (commentId) => {
      try {
        const response = await reactionService.acceptSolution(updateId, commentId);
        setAcceptedSolution(response.data);
        toast.success("Solution accepted");
      } catch {
        toast.error("Failed to accept solution");
      }
    },
    [updateId],
  );

  const handleRemoveAcceptedSolution = useCallback(async () => {
    try {
      await reactionService.removeAcceptedSolution(updateId);
      setAcceptedSolution(null);
      toast.success("Solution removed");
    } catch {
      toast.error("Failed to remove solution");
    }
  }, [updateId]);

  const isOwner = currentUser?.id === update?.journey_owner?.id;
  const milestoneLabel = update ? MILESTONE_LABELS[update.milestone_status] : "";
  const milestoneColor = update ? MILESTONE_COLORS[update.milestone_status] : "";
  const owner = update?.journey_owner;
  const initials = owner?.username?.charAt(0)?.toUpperCase() || "U";

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!update) {
    return (
      <div className="text-center py-16">
        <p className="text-muted-foreground">Update not found.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3 min-w-0">
          <Button variant="ghost" size="icon" asChild>
            <Link to={`/journeys/${journeyId}`}>
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <h1 className="text-2xl font-bold tracking-tight truncate">{update.title}</h1>
        </div>
        {isOwner && (
          <div className="flex items-center gap-2 shrink-0">
            <Button asChild variant="outline" size="sm">
              <Link
                to={`/journeys/${journeyId}/updates/${updateId}/edit`}
                className="inline-flex items-center gap-2 whitespace-nowrap"
              >
                <Edit className="h-4 w-4 mr-1" />
                Edit
              </Link>
            </Button>
            <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" size="sm">
                  <Trash2 className="h-4 w-4 mr-1" />
                  Delete
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete Update</AlertDialogTitle>
                  <AlertDialogDescription>
                    Are you sure you want to delete this update? This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={handleDelete}
                    disabled={deleting}
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  >
                    {deleting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    Delete
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        )}
      </div>

      {acceptedSolution && (
        <Card className="mb-6 border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950/20">
          <CardContent className="p-4 flex items-center gap-3">
            <CheckCircle className="h-5 w-5 text-emerald-600" />
            <div>
              <p className="text-sm font-medium">Solution Accepted</p>
              <p className="text-xs text-muted-foreground">
                Accepted by{" "}
                <Link
                  to={`/profile/${acceptedSolution.accepted_by?.username}`}
                  className="text-primary hover:underline"
                >
                  {acceptedSolution.accepted_by?.username}
                </Link>
              </p>
            </div>
            {isOwner && (
              <Button
                variant="outline"
                size="sm"
                className="ml-auto"
                onClick={handleRemoveAcceptedSolution}
              >
                <X className="h-4 w-4 mr-1" />
                Remove
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardContent className="p-4 flex items-center gap-4">
              <Avatar className="h-10 w-10">
                <AvatarImage src={owner?.avatar_url} alt={owner?.username} />
                <AvatarFallback>{initials}</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">{owner?.username}</p>
                <Link
                  to={`/profile/${owner?.username}`}
                  className="text-xs text-muted-foreground hover:text-primary hover:underline"
                >
                  View profile →
                </Link>
              </div>
              <div className="ml-auto flex items-center gap-2 text-xs text-muted-foreground">
                <span>
                  Posted {formatDistanceToNow(new Date(update.created_at), { addSuffix: true })}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Description */}
          <Card>
            <CardContent className="p-5">
              <div
                className="prose prose-sm max-w-none dark:prose-invert"
                dangerouslySetInnerHTML={{
                  __html: update.description || "No description provided.",
                }}
              />
            </CardContent>
          </Card>

          {/* Meta Info */}
          <Card>
            <CardContent className="p-5 space-y-4">
              <div className="flex flex-wrap gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <span className="font-medium">Progress:</span>
                  <span className="text-muted-foreground">{update.progress_percentage}%</span>
                  <Progress value={update.progress_percentage || 0} className="w-24 h-2" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">Milestone:</span>
                  <Badge className={milestoneColor}>{milestoneLabel}</Badge>
                </div>
                {update.help_needed && (
                  <div className="flex items-center gap-2">
                    <Badge className="bg-orange-100 text-orange-700">Help Needed</Badge>
                  </div>
                )}
                {update.visibility && (
                  <div className="flex items-center gap-2">
                    <span className="font-medium">Visibility:</span>
                    <Badge variant="outline">{update.visibility}</Badge>
                  </div>
                )}
              </div>

              <Separator />

              <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  Created {formatDistanceToNow(new Date(update.created_at), { addSuffix: true })}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  Updated {formatDistanceToNow(new Date(update.updated_at), { addSuffix: true })}
                </span>
              </div>

              <Separator />

              <div className="flex items-center gap-4 text-sm">
                {!isOwner && (
                  <button
                    onClick={handleLike}
                    disabled={liking}
                    className="flex items-center gap-1 rounded-md px-2 py-1 transition-colors hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {isLiked ? (
                      <Heart className="h-4 w-4 fill-red-500 text-red-500" />
                    ) : (
                      <Heart className="h-4 w-4" />
                    )}
                    <span>{likeCount}</span>
                  </button>
                )}

                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex items-center gap-1 rounded-md px-2 py-1 transition-colors hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isSaved ? (
                    <BookmarkCheck className="h-4 w-4 text-primary" />
                  ) : (
                    <Bookmark className="h-4 w-4" />
                  )}
                  <span className="hidden sm:inline">{isSaved ? "Saved" : "Save"}</span>
                </button>

                <button
                  onClick={() => setCommentsDialogOpen(true)}
                  className="flex items-center gap-1 rounded-md px-2 py-1 transition-colors hover:bg-muted"
                >
                  <MessageCircle className="h-4 w-4" />
                  <span>{update.comment_count ?? 0}</span>
                </button>
                {!isOwner && (
                  <ReportDialog
                    contentType="journeyupdate"
                    objectId={updateId}
                    trigger={
                      <button className="flex items-center gap-1 rounded-md px-2 py-1 transition-colors hover:bg-muted">
                        <Flag className="h-4 w-4" />
                        <span className="hidden sm:inline">Report</span>
                      </button>
                    }
                  />
                )}
              </div>
            </CardContent>
          </Card>

          {/* Tags */}
          <Card>
            <CardContent className="p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium">Tags</h3>
                {isOwner && (
                  <div className="flex items-center gap-2">
                    <Input
                      placeholder="Add tag..."
                      value={tags.inputValue || ""}
                      onChange={(e) => tags.setInputValue(e.target.value)}
                      className="h-8 w-32 text-sm"
                      disabled={tags.loading}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          tags.addTag(tags.inputValue);
                          tags.setInputValue("");
                        }
                      }}
                    />
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="outline" size="sm" className="h-8 px-2">
                          <Plus className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-48 max-h-60 overflow-y-auto">
                        {tags.trending.length === 0 && (
                          <DropdownMenuItem disabled>No trending tags</DropdownMenuItem>
                        )}
                        {tags.trending.map((tag) => (
                          <DropdownMenuItem
                            key={tag.id}
                            onClick={() => {
                              tags.addTag(tag.name);
                              tags.setInputValue("");
                            }}
                            disabled={tags.tags.some((t) => t.name === tag.name)}
                          >
                            #{tag.name}{" "}
                            <span className="ml-auto text-xs text-muted-foreground">
                              {tag.usage_count}
                            </span>
                          </DropdownMenuItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>
                    <Button
                      size="sm"
                      variant="secondary"
                      className="h-8"
                      onClick={() => {
                        tags.addTag(tags.inputValue);
                        tags.setInputValue("");
                      }}
                      disabled={!tags.inputValue?.trim() || tags.loading}
                    >
                      Add
                    </Button>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap gap-1.5">
                {tags.tags.length === 0 && (
                  <span className="text-sm text-muted-foreground">No tags yet</span>
                )}
                {tags.tags.map((tag) => (
                  <Badge
                    key={tag.id || tag.name}
                    variant="secondary"
                    className="text-xs rounded-full px-3 py-1"
                  >
                    #{tag.name}
                    {isOwner && (
                      <button
                        onClick={() => tags.removeTag(tag.name)}
                        className="ml-1.5 hover:text-destructive transition-colors"
                        disabled={tags.loading}
                      >
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right column: Images Carousel */}
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="p-5">
              <h3 className="text-sm font-medium mb-3">Images</h3>
              {images.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-48 rounded-lg border border-dashed bg-muted/20 text-muted-foreground">
                  <p className="text-sm">No images</p>
                </div>
              ) : images.length === 1 ? (
                <img
                  src={images[0].cloudinary_url}
                  alt="Update"
                  className="w-full h-48 object-cover rounded-lg"
                />
              ) : (
                <Carousel className="w-full">
                  <CarouselContent>
                    {images.map((img) => (
                      <CarouselItem key={img.id}>
                        <img
                          src={img.cloudinary_url}
                          alt="Update"
                          className="w-full h-48 object-cover rounded-lg"
                        />
                      </CarouselItem>
                    ))}
                  </CarouselContent>
                  <CarouselPrevious className="left-2" />
                  <CarouselNext className="right-2" />
                </Carousel>
              )}
              {images.length > 1 && (
                <p className="text-center text-xs text-muted-foreground mt-2">
                  {images.length} images
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Comments Dialog */}
      <Dialog open={commentsDialogOpen} onOpenChange={setCommentsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>Comments</DialogTitle>
          </DialogHeader>

          {/* New comment form */}
          <div className="flex gap-2">
            <Input
              placeholder="Write a comment..."
              value={comments.newCommentContent || ""}
              onChange={(e) => comments.setNewCommentContent(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  comments.addComment(comments.newCommentContent);
                }
              }}
              disabled={comments.loading}
            />
            <Button
              onClick={() => comments.addComment(comments.newCommentContent)}
              disabled={comments.loading || !comments.newCommentContent?.trim()}
            >
              {comments.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Post"}
            </Button>
          </div>

          {/* Comments list */}
          <div className="flex-1 overflow-y-auto space-y-4 mt-4">
            {comments.loading && comments.comments.length === 0 ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : comments.comments.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">
                No comments yet. Be the first!
              </p>
            ) : (
              comments.comments.map((comment) => (
                <CommentItem
                  key={comment.id}
                  comment={comment}
                  currentUser={currentUser}
                  isOwner={isOwner}
                  helpNeeded={update.help_needed}
                  acceptedSolution={acceptedSolution}
                  onAcceptSolution={handleAcceptSolution}
                  onDeleteComment={comments.deleteComment}
                  onUpdateComment={comments.editComment}
                  onAddReply={comments.addReply}
                  onUpdateReply={comments.editReply}
                  onDeleteReply={comments.deleteReply}
                />
              ))
            )}
            {comments.hasMore && (
              <div className="flex justify-center py-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => comments.fetchComments(comments.cursor)}
                  disabled={comments.loading}
                >
                  {comments.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Load more"}
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
