import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { authService } from "@/services/auth";
import { toast } from "sonner";
import { Search, Loader2, X } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Explore() {
  const { user } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchPerformed, setSearchPerformed] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    const trimmed = searchQuery.trim();
    if (!trimmed) {
      toast.warning("Please enter a username to search");
      return;
    }

    setLoading(true);
    setSearchPerformed(true);
    try {
      const response = await authService.searchUsers(trimmed);

      const users = Array.isArray(response.data)
        ? response.data
        : response.data
          ? [response.data]
          : [];

      setUsers(users);
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to search users");
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery("");
    setUsers([]);
    setSearchPerformed(false);
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Explore Users</h1>
        <p className="text-sm text-muted-foreground">Find and follow other builders</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by username..."
            className="pl-9 pr-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <Button type="submit" disabled={loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Search"}
        </Button>
      </form>

      {searchPerformed ? (
        loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : users.length === 0 ? (
          <div className="py-12 text-center">
            <p className="text-muted-foreground">No users found.</p>
            <p className="text-sm text-muted-foreground">Try a different search term.</p>
          </div>
        ) : (
          <>
            <p className="text-sm text-muted-foreground">
              Found {users.length} user{users.length !== 1 ? "s" : ""}
            </p>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {users.map((u) => (
                <UserCard key={u.id} user={u} currentUser={user} />
              ))}
            </div>
          </>
        )
      ) : (
        <div className="py-12 text-center text-muted-foreground">
          <Search className="mx-auto h-12 w-12 opacity-20" />
          <p className="mt-4">Search for users to get started</p>
        </div>
      )}
    </div>
  );
}

function UserCard({ user: u }) {
  const initials = u.username?.charAt(0)?.toUpperCase() || "U";

  return (
    <Card className="transition hover:shadow-md">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <Link to={`/profile/${u.username}`} className="flex min-w-0 flex-1 items-center gap-3">
            <Avatar className="h-12 w-12 shrink-0">
              <AvatarImage src={u.profile?.avatar_url} alt={u.username} />
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium hover:underline">{u.username}</p>
              <p className="truncate text-sm text-muted-foreground">
                {u.first_name || ""} {u.last_name || ""}
              </p>
              <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                <span>{u.follower_count || 0} followers</span>
                {u.is_verified && <Badge className="bg-green-600 text-[10px]">✓ Verified</Badge>}
              </div>
            </div>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
