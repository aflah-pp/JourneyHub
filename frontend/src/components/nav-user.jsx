"use client";

import { Link } from "react-router-dom";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

import { ChevronsUpDown, LogOut } from "lucide-react";

export function NavUser({ user, items = [], onLogout }) {
  const { isMobile } = useSidebar();

  const avatarFallback = user?.name?.trim()?.charAt(0)?.toUpperCase() || "U";

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger
            render={<SidebarMenuButton size="lg" className="aria-expanded:bg-muted" />}
          >
            <Avatar className="size-8">
              <AvatarImage src={user?.avatar || ""} alt={user?.name || "User"} />
              <AvatarFallback>{avatarFallback}</AvatarFallback>
            </Avatar>

            <div className="grid min-w-0 flex-1 text-left text-sm leading-tight">
              <span className="truncate font-medium">{user?.name || "User"}</span>
              <span className="truncate text-xs text-muted-foreground">{user?.email || ""}</span>
            </div>

            <ChevronsUpDown className="ml-auto size-4 opacity-60" />
          </DropdownMenuTrigger>

          <DropdownMenuContent
            className="w-64"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={6}
          >
            <div className="flex items-center gap-3 px-3 py-3">
              <Avatar className="size-10">
                <AvatarImage src={user?.avatar} alt={user?.name || "User"} />
                <AvatarFallback>{avatarFallback}</AvatarFallback>
              </Avatar>

              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{user?.name || "User"}</p>
                <p className="truncate text-xs text-muted-foreground">{user?.email || ""}</p>
              </div>
            </div>

            <DropdownMenuSeparator />

            {items.length > 0 && (
              <>
                <DropdownMenuGroup>
                  {items.map((item) => {
                    const Icon = item.icon;

                    return (
                      <DropdownMenuItem key={item.to} render={<Link to={item.to} />}>
                        {Icon && <Icon className="size-4" />}
                        <span>{item.label}</span>
                      </DropdownMenuItem>
                    );
                  })}
                </DropdownMenuGroup>

                <DropdownMenuSeparator />
              </>
            )}

            <DropdownMenuItem variant="destructive" onClick={onLogout}>
              <LogOut className="size-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
