import { useEffect, useState } from "react";
import { auditService } from "@/services/auth";
import { toast } from "sonner";
import {
  Loader2,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  Eye,
  Shield,
  X,
  ChevronRight,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Dialog, DialogContent, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

const STATUS_CONFIG = {
  PENDING: {
    label: "Pending",
    color:
      "bg-yellow-500/10 text-yellow-600 border-yellow-500/20 dark:bg-yellow-500/20 dark:text-yellow-400",
    icon: Clock,
    dot: "bg-yellow-500",
  },
  UNDER_REVIEW: {
    label: "Under Review",
    color: "bg-blue-500/10 text-blue-600 border-blue-500/20 dark:bg-blue-500/20 dark:text-blue-400",
    icon: Eye,
    dot: "bg-blue-500",
  },
  RESOLVED: {
    label: "Resolved",
    color:
      "bg-green-500/10 text-green-600 border-green-500/20 dark:bg-green-500/20 dark:text-green-400",
    icon: CheckCircle,
    dot: "bg-green-500",
  },
  DISMISSED: {
    label: "Dismissed",
    color: "bg-gray-500/10 text-gray-600 border-gray-500/20 dark:bg-gray-500/20 dark:text-gray-400",
    icon: X,
    dot: "bg-gray-500",
  },
  NEEDS_INFO: {
    label: "Needs Info",
    color:
      "bg-orange-500/10 text-orange-600 border-orange-500/20 dark:bg-orange-500/20 dark:text-orange-400",
    icon: AlertTriangle,
    dot: "bg-orange-500",
  },
};

const TARGET_TYPE_LABELS = {
  journey: "Journey",
  journeyupdate: "Update",
  comment: "Comment",
  commentreply: "Reply",
};

const REASON_LABELS = {
  SPAM: "Spam",
  HARASSMENT: "Harassment",
  INAPPROPRIATE: "Inappropriate",
  COPYRIGHT: "Copyright",
  PRIVACY: "Privacy",
  OTHER: "Other",
};

function ReportsSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-28 rounded-xl" />
        ))}
      </div>
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-24 w-full rounded-xl" />
        ))}
      </div>
    </div>
  );
}

function StatsCard({ icon: Icon, label, value, color }) {
  return (
    <Card className="overflow-hidden border-0 shadow-sm transition hover:shadow-md">
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{label}</p>
            <p className="mt-1.5 text-3xl font-bold tracking-tight">{value || 0}</p>
          </div>
          <div className={cn("rounded-full p-3", color)}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ReportStatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.PENDING;
  const Icon = config.icon;

  return (
    <Badge
      variant="outline"
      className={cn(
        "flex items-center gap-1.5 px-3 py-1 text-xs font-medium transition-all",
        config.color,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", config.dot)} />
      <Icon className="h-3 w-3" />
      {config.label}
    </Badge>
  );
}

function ReportDetailDialog({ report, children }) {
  if (!report) return null;

  const targetLabel = TARGET_TYPE_LABELS[report.target_type] || report.target_type;
  const reasonLabel = REASON_LABELS[report.reason] || report.reason;

  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="max-w-2xl p-0 overflow-hidden">
        <div className="border-b bg-muted/30 px-6 py-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <DialogTitle className="flex items-center gap-2 text-xl">
                <Shield className="h-5 w-5 text-destructive" />
                Report Details
              </DialogTitle>
              <p className="mt-1 text-sm text-muted-foreground">
                Review the submitted report and moderation information.
              </p>
            </div>
            <ReportStatusBadge status={report.status} />
          </div>
        </div>

        <div className="p-6">
          <dl className="divide-y">
            <div className="py-4">
              <dt className="text-sm font-medium text-muted-foreground">Reporter</dt>
              <dd className="mt-2 flex items-center gap-3">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={report.reporter?.avatar_url} />
                  <AvatarFallback>
                    {report.reporter?.username?.charAt(0)?.toUpperCase() || "U"}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium">{report.reporter?.username}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDistanceToNow(new Date(report.created_at), { addSuffix: true })}
                  </p>
                </div>
              </dd>
            </div>

            <div className="py-4">
              <dt className="text-sm font-medium text-muted-foreground">Target</dt>
              <dd className="mt-2">
                <Badge variant="secondary">{targetLabel}</Badge>
                <p className="mt-2 font-mono text-sm break-all">{report.target_id}</p>
              </dd>
            </div>

            <div className="py-4">
              <dt className="text-sm font-medium text-muted-foreground">Reason</dt>
              <dd className="mt-2">{reasonLabel}</dd>
            </div>

            {report.description && (
              <div className="py-4">
                <dt className="text-sm font-medium text-muted-foreground">Description</dt>
                <dd className="mt-2 whitespace-pre-wrap rounded-lg bg-muted/40 p-4 text-sm">
                  {report.description}
                </dd>
              </div>
            )}

            {report.moderator && (
              <div className="py-4">
                <dt className="text-sm font-medium text-muted-foreground">Moderator</dt>
                <dd className="mt-2 flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={report.moderator?.avatar_url} />
                    <AvatarFallback>
                      {report.moderator?.username?.charAt(0)?.toUpperCase() || "M"}
                    </AvatarFallback>
                  </Avatar>
                  <span className="font-medium">{report.moderator?.username}</span>
                </dd>
              </div>
            )}

            {report.resolution_note && (
              <div className="py-4">
                <dt className="text-sm font-medium text-muted-foreground">Resolution Note</dt>
                <dd className="mt-2 whitespace-pre-wrap rounded-lg bg-muted/40 p-4 text-sm">
                  {report.resolution_note}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default function Reports() {
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState([]);
  const [, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [stats, setStats] = useState(null);
  const [statusFilter, setStatusFilter] = useState("");
  const pageSize = 20;

  const fetchReports = async (pageNum = 1, reset = false) => {
    setLoading(true);
    try {
      const params = {
        page: pageNum,
        page_size: pageSize,
        status: statusFilter || undefined,
      };
      const response = await auditService.getReports(params);
      const data = response.data;
      const results = data.results || [];

      if (reset || pageNum === 1) {
        setReports(results);
      } else {
        setReports((prev) => [...prev, ...results]);
      }

      setTotal(data.count || 0);
      setHasNext(!!data.next);
      setPage(pageNum);
    } catch (err) {
      console.error("Failed to load reports:", err);
      toast.error("Failed to load reports");
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await auditService.getReportStats();
      setStats(response.data);
    } catch (err) {
      console.error("Failed to load stats:", err);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchReports(1, true);
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchReports(1, true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const loadMore = () => {
    if (!hasNext || loading) return;
    fetchReports(page + 1);
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <div className="rounded-full bg-primary/10 p-2 text-primary">
            <Shield className="h-5 w-5" />
          </div>
          Reports
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Monitor and manage content reports across the platform
        </p>
      </div>

      {/* ── Stats ── */}
      {stats ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            icon={FileText}
            label="Total Reports"
            value={stats.total}
            color="bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"
          />
          <StatsCard
            icon={Clock}
            label="Pending"
            value={stats.pending}
            color="bg-yellow-100 text-yellow-600 dark:bg-yellow-950/50 dark:text-yellow-400"
          />
          <StatsCard
            icon={Eye}
            label="Under Review"
            value={stats.under_review}
            color="bg-blue-100 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400"
          />
          <StatsCard
            icon={CheckCircle}
            label="Resolved"
            value={stats.resolved}
            color="bg-green-100 text-green-600 dark:bg-green-950/50 dark:text-green-400"
          />
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-xl" />
          ))}
        </div>
      )}

      {/* ── Filters ── */}
      <div className="flex flex-wrap items-center gap-3">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Statuses</SelectItem>
            <SelectItem value="PENDING">Pending</SelectItem>
            <SelectItem value="UNDER_REVIEW">Under Review</SelectItem>
            <SelectItem value="RESOLVED">Resolved</SelectItem>
            <SelectItem value="DISMISSED">Dismissed</SelectItem>
            <SelectItem value="NEEDS_INFO">Needs Info</SelectItem>
          </SelectContent>
        </Select>

        {statusFilter && (
          <Button variant="ghost" size="sm" onClick={() => setStatusFilter("")} className="gap-1">
            <X className="h-3 w-3" />
            Clear
          </Button>
        )}
      </div>

      {/* ── List ── */}
      {loading && reports.length === 0 ? (
        <ReportsSkeleton />
      ) : reports.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="py-16 text-center">
            <div className="mx-auto rounded-full bg-muted/50 p-4 w-16 h-16 flex items-center justify-center">
              <AlertTriangle className="h-8 w-8 text-muted-foreground/40" />
            </div>
            <p className="mt-4 text-lg font-medium text-muted-foreground">No reports found</p>
            <p className="text-sm text-muted-foreground">
              {statusFilter ? "Try adjusting your filters" : "All clear — no reports to review"}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {reports.map((report) => (
            <ReportDetailDialog key={report.id} report={report}>
              <div className="group cursor-pointer rounded-xl border bg-card p-5 transition-all duration-200 hover:border-primary/30 hover:bg-muted/30 hover:shadow-md">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex flex-1 gap-4 min-w-0">
                    <Avatar className="h-11 w-11 shrink-0 ring-1 ring-border">
                      <AvatarImage src={report.reporter?.avatar_url} />
                      <AvatarFallback>
                        {report.reporter?.username?.charAt(0)?.toUpperCase() || "U"}
                      </AvatarFallback>
                    </Avatar>

                    <div className="min-w-0 flex-1 space-y-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-semibold truncate">{report.reporter?.username}</span>
                        <span className="text-muted-foreground">reported a</span>
                        <Badge variant="outline">
                          {TARGET_TYPE_LABELS[report.target_type] || report.target_type}
                        </Badge>
                      </div>

                      <div className="flex flex-wrap items-center gap-2 text-sm">
                        <span className="text-muted-foreground">Reason:</span>
                        <Badge variant="secondary">
                          {REASON_LABELS[report.reason] || report.reason}
                        </Badge>
                      </div>

                      <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
                        <span>
                          ID: <span className="font-mono">{report.target_id?.slice(0, 8)}</span>
                        </span>
                        <span>
                          {formatDistanceToNow(new Date(report.created_at), {
                            addSuffix: true,
                          })}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-3 shrink-0">
                    <ReportStatusBadge status={report.status} />
                    <ChevronRight className="h-4 w-4 text-muted-foreground transition-all group-hover:translate-x-1 group-hover:text-primary" />
                  </div>
                </div>
              </div>
            </ReportDetailDialog>
          ))}
        </div>
      )}

      {hasNext && (
        <div className="flex justify-center pt-4">
          <Button
            variant="outline"
            onClick={loadMore}
            disabled={loading}
            className="w-full max-w-sm gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading...
              </>
            ) : (
              "Load more reports"
            )}
          </Button>
        </div>
      )}
    </div>
  );
}
