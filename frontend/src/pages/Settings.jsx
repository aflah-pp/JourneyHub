import { Outlet, NavLink } from "react-router-dom";
import { User, Bell, Trash2, ArrowLeft, Trash } from "lucide-react";

import { Button } from "@/components/ui/button";

import { cn } from "@/lib/utils";

const settingsNavItems = [
  {
    title: "Profile",
    to: "/settings/profile",
    icon: <User className="h-4 w-4" />,
  },
  {
    title: "Preferences",
    to: "/settings/preferences",
    icon: <Bell className="h-4 w-4" />,
  },
  {
    title: "Clear Data",
    to: "/settings/clear-data",
    icon: <Trash className="h-4 w-4" />,
  },
  {
    title: "Delete Account",
    to: "/settings/delete-account",
    icon: <Trash2 className="h-4 w-4" />,
  },
];

export default function Settings() {
  return (
    <div className=" max-w-5xl space-y-9 px-4 py-10">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <NavLink to="/dashboard">
            <ArrowLeft className="h-5 w-5" />
          </NavLink>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
          <p className="text-sm text-muted-foreground">
            Manage your account settings and preferences
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-6 md:flex-row md:gap-8">
        <aside className="w-full md:w-56 shrink-0">
          <nav className="flex flex-row gap-1 overflow-x-auto md:flex-col">
            {settingsNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors whitespace-nowrap",
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )
                }
              >
                {item.icon}
                {item.title}
              </NavLink>
            ))}
          </nav>
        </aside>

        <div className="flex-1">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
