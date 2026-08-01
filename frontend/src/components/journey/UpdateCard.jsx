import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Heart, MessageCircle, Clock, HelpCircle, FolderTree } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { MILESTONE_BADGE } from "./JourneyConstants";

export function UpdateCard({ update, journeyId }) {
  const milestoneInfo = update.milestone_status ? MILESTONE_BADGE[update.milestone_status] : null;
  const imageUrl = update.image?.cloudinary_url || null;

  return (
    <Link to={`/journeys/${journeyId}/updates/${update.id}`} className="group block">
      <div className="flex items-start gap-4 p-3 rounded-xl border bg-card transition-all hover:bg-muted/50 hover:border-primary/30 hover:shadow-sm">
        <div className="w-36 h-24 shrink-0 rounded-lg overflow-hidden bg-muted/50">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={update.title}
              className="w-full h-full object-cover transition-transform group-hover:scale-105"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-muted-foreground/40">
              <FolderTree className="h-8 w-8" />
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0 space-y-1.5">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-sm group-hover:text-primary transition-colors truncate">
              {update.title}
            </h3>
            <div className="flex flex-wrap gap-1 shrink-0">
              {milestoneInfo && (
                <Badge className={`text-[10px] ${milestoneInfo.color}`}>
                  {milestoneInfo.label}
                </Badge>
              )}
              {update.help_needed && (
                <Badge className="bg-orange-500/10 text-orange-600 border-orange-500/20 text-[10px] flex items-center gap-0.5">
                  <HelpCircle className="h-3 w-3" />
                  Help
                </Badge>
              )}
            </div>
          </div>

          {update.description && (
            <p className="text-xs text-muted-foreground line-clamp-2">
              {update.description.replace(/<[^>]*>/g, "")}
            </p>
          )}

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[10px] text-muted-foreground">
            <span className="flex items-center gap-1">
              <Heart className="h-3 w-3" />
              {update.like_count || 0}
            </span>
            <span className="flex items-center gap-1">
              <MessageCircle className="h-3 w-3" />
              {update.comment_count || 0}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatDistanceToNow(new Date(update.created_at), { addSuffix: true })}
            </span>
            {update.progress_percentage > 0 && (
              <span className="flex items-center gap-1">
                <Progress value={update.progress_percentage} className="h-1 w-12" />
                {update.progress_percentage}%
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
