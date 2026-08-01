import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Calendar, Clock, Eye, FolderTree } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { STATUS_COLORS, CATEGORY_LABELS } from "./journeyConstants";

export function JourneyInfoPanel({ journey }) {
  const initials = journey.owner?.username?.charAt(0)?.toUpperCase() || "U";

  return (
    <aside className="space-y-6 overflow-y-auto pb-4 pr-2 scrollbar-thin">
      {/* Cover Image */}
      <Card className="overflow-hidden">
        {journey.cover_image_url ? (
          <img
            src={journey.cover_image_url}
            alt={journey.title}
            className="aspect-video w-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="aspect-video w-full bg-muted/30 flex items-center justify-center">
            <FolderTree className="h-12 w-12 text-muted-foreground/40" />
          </div>
        )}
      </Card>

      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">{journey.title}</h2>
          {journey.description && (
            <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
              {journey.description}
            </p>
          )}
        </div>

        <div className="flex items-center gap-3 p-3 rounded-lg border bg-card/50">
          <Avatar className="h-10 w-10">
            <AvatarImage src={journey.owner?.avatar_url} alt={journey.owner?.username} />
            <AvatarFallback className="text-xs">{initials}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium">{journey.owner?.username}</p>
            <div className="flex flex-wrap gap-x-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                Started {formatDistanceToNow(new Date(journey.created_at), { addSuffix: true })}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Updated {formatDistanceToNow(new Date(journey.updated_at), { addSuffix: true })}
              </span>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <Badge
            variant="outline"
            className={`text-xs font-medium ${STATUS_COLORS[journey.status] || ""}`}
          >
            {journey.status}
          </Badge>
          <Badge variant="secondary" className="text-xs rounded-full">
            {CATEGORY_LABELS[journey.category] || journey.category}
          </Badge>
          <Badge variant="outline" className="text-xs rounded-full">
            <Eye className="mr-1 h-3 w-3" />
            {journey.visibility}
          </Badge>
        </div>

        <div>
          <div className="flex items-center justify-between text-sm mb-1.5">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{journey.latest_progress || 0}%</span>
          </div>
          <Progress value={journey.latest_progress || 0} className="h-2.5" />
          <div className="mt-2 text-xs text-muted-foreground">
            {journey.update_count || 0} updates
          </div>
        </div>

        {journey.tags && journey.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-2 border-t">
            {journey.tags.map((tag) => (
              <Badge key={tag.id} variant="secondary" className="text-xs rounded-full">
                #{tag.name}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
