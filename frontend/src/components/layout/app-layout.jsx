"use client";

import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { authService, notificationService } from "@/services/auth";
import { toast } from "sonner";
import { Bell, Sun, Moon } from "lucide-react";

import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/context/ThemeContext";
import { AppSidebar } from "@/components/app-sidebar";
import { useEffect, useState } from "react";

export function AppLayout() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { theme, toggleTheme } = useTheme();
  const [unreadCount, setUnreadCount] = useState(0);

  const handleLogout = async () => {
    try {
      await authService.logout();
    } catch (err) {
      console.error(err);
    } finally {
      logout();
      toast.success("Logged out");
      navigate("/login", { replace: true });
    }
  };

  useEffect(() => {
    const fetchUnread = async () => {
      try {
        const res = await notificationService.getUnreadCount();
        setUnreadCount(res.data?.unread_count || 0);
        // eslint-disable-next-line no-unused-vars
      } catch (e) {
        // ignore
      }
    };
    fetchUnread();
  }, []);

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <AppSidebar user={user} onLogout={handleLogout} />
        <div className="flex flex-1 flex-col">
          <header className="sticky top-0 z-10 flex h-16 items-center gap-4 bg-background/80 border-b px-4 md:px-6">
            <SidebarTrigger />
            <div className="ml-auto flex items-center gap-2">
              <Button variant="ghost" size="icon" onClick={toggleTheme}>
                {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
                <span className="sr-only">Toggle theme</span>
              </Button>
              <Link to="/notifications" className="relative">
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-medium text-white">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </Link>
            </div>
          </header>

          <main className="flex-1 p-4 md:p-5">
          {/* <main className="flex flex-1 flex-col overflow-hidden p-4 md:p-5"> */}
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
