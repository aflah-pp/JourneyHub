import { Link } from "react-router-dom";
import {
  LayoutDashboard,
  FolderTree,
  Rss,
  Compass,
  LifeBuoy,
  Send,
  BadgeCheck,
  Bell,
  Sparkles,
  Bolt,
  Star,
  NotepadText,
  FileText,
  Shield,
} from "lucide-react";

import { NavMain } from "@/components/nav-main";
import { NavSecondary } from "@/components/nav-secondary";
import { NavUser } from "@/components/nav-user";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const navMainItems = [
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: <LayoutDashboard className="size-4" />,
  },
  {
    title: "Journeys",
    url: "/journeys",
    icon: <FolderTree className="size-4" />,
  },
  {
    title: "Feed",
    icon: <Rss className="size-4" />,
    items: [
      { title: "Latest", url: "/feed/latest" },
      { title: "Following", url: "/feed/following" },
      { title: "Trending", url: "/feed/trending" },
      { title: "Help Needed", url: "/feed/help-needed" },
    ],
  },
  {
    title: "Explore",
    icon: <Compass className="size-4" />,
    items: [
      { title: "Users", url: "/explore/users" },
      { title: "Journey", url: "/explore/journeys" },
      { title: "Trending Tags", url: "/explore/trending-tags" },
    ],
  },
  {
    title: "Score",
    icon: <Star className="size-4" />,
    items: [
      { title: "My Score", url: "/score/self" },
      { title: "Leaderboard", url: "/score/leaderboard" },
    ],
  },
];

const navSecondaryItems = [
  {
    title: "Support",
    url: "/support",
    icon: <LifeBuoy className="size-4" />,
  },
  {
    title: "Feedback",
    url: "/feedback",
    icon: <Send className="size-4" />,
  },
  {
    title: "Pricing",
    url: "/pricing",
    icon: <Sparkles className="size-4" />,
  },
  {
    title: "Terms",
    url: "/terms",
    icon: <FileText className="size-4" />,
  },
  {
    title: "Privacy",
    url: "/privacy",
    icon: <Shield className="size-4" />,
  },
];

export function AppSidebar({ user, onLogout, ...props }) {
  const userData = {
    name: user?.username || "User",
    email: user?.email || "",
    avatar: user?.profile?.avatar_url || "",
  };

  const userMenuItems = [
    {
      label: "Upgrade to Pro",
      to: "/pricing",
      icon: Sparkles,
    },
    {
      label: "Account",
      to: "/account",
      icon: BadgeCheck,
    },
    {
      label: "Notifications",
      to: "/notifications",
      icon: Bell,
    },
    {
      label: "Report Logs",
      to: "/logs",
      icon: NotepadText,
    },
    {
      label: "Settings",
      to: "/settings",
      icon: Bolt,
    },
  ];

  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" render={<Link to="/dashboard" />}>
              <div className="flex aspect-square size-9 items-center justify-center overflow-hidden rounded-lg">
                <img
                  src="/journeyhub.png"
                  alt="JourneyHub"
                  className="h-full w-full object-cover"
                />
              </div>

              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-medium">JourneyHub</span>
                <span className="truncate text-xs">Build your journey</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <NavMain items={navMainItems} />
        <NavSecondary items={navSecondaryItems} className="mt-auto" />
      </SidebarContent>

      <SidebarFooter>
        <NavUser user={userData} items={userMenuItems} onLogout={onLogout} />
      </SidebarFooter>
    </Sidebar>
  );
}
