import { Skeleton } from "@/components/ui/skeleton";

export function JourneyDetailSkeleton() {
  return (
    <div className="flex flex-col h-full min-h-0 overflow-hidden max-w-[1600px] mx-auto px-8 py-4 w-full">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4 shrink-0">
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-10 rounded-full" />
          <Skeleton className="h-8 w-48" />
        </div>
        <div className="flex items-center gap-2">
          <Skeleton className="h-9 w-20" />
          <Skeleton className="h-9 w-20" />
          <Skeleton className="h-9 w-20" />
        </div>
      </div>
      <div className="flex-1 min-h-0 overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-[380px_1fr] h-full gap-8">
          <div className="space-y-6 overflow-y-auto pb-4 pr-2">
            <Skeleton className="aspect-video rounded-xl" />
            <Skeleton className="h-64 rounded-xl" />
          </div>
          <div className="space-y-6 overflow-y-auto pb-4 pr-2">
            <div className="flex items-center justify-between sticky top-0 bg-background/95 backdrop-blur-sm z-10 py-2">
              <Skeleton className="h-7 w-32" />
              <Skeleton className="h-9 w-24" />
            </div>
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-24 w-full rounded-xl" />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
