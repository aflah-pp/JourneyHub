export const STATUS_COLORS = {
  ACTIVE: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20",
  PAUSED: "bg-amber-500/10 text-amber-600 border-amber-500/20",
  COMPLETED: "bg-blue-500/10 text-blue-600 border-blue-500/20",
  ABANDONED: "bg-rose-500/10 text-rose-600 border-rose-500/20",
};

export const CATEGORY_LABELS = {
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

export const MILESTONE_BADGE = {
  NONE: null,
  MILESTONE: { label: "Milestone", color: "bg-violet-500/10 text-violet-600 border-violet-500/20" },
  COMPLETED: {
    label: "Completed",
    color: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20",
  },
  IN_PROGRESS: {
    label: "In Progress",
    color: "bg-amber-500/10 text-amber-600 border-amber-500/20",
  },
  FAILED: { label: "Failed", color: "bg-rose-500/10 text-rose-600 border-rose-500/20" },
};
