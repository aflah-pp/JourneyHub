import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Loader2, AlertTriangle, Trash2 } from "lucide-react";

import { useAuthStore } from "@/store/authStore";
import { authService } from "@/services/auth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export default function DeleteAccount() {
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const [confirmText, setConfirmText] = useState("");
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  const handleDelete = async () => {
    if (confirmText.trim().toLowerCase() !== "delete") {
      toast.error('Please type "delete" to confirm');
      return;
    }

    setLoading(true);
    try {
      await authService.deleteAccount(confirmText.trim().toLowerCase());
      toast.success("Account deleted successfully");
      logout();
      navigate("/login");
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to delete account");
    } finally {
      setLoading(false);
      setOpen(false);
    }
  };

  return (
    <Card className="border-destructive/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-destructive">
          <AlertTriangle className="h-5 w-5" />
          Delete Account
        </CardTitle>
        <CardDescription>
          Permanently delete your account and all associated data. This action cannot be undone.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="rounded-lg bg-destructive/10 p-4 text-sm text-destructive">
          <p className="font-medium">Warning:</p>
          <ul className="mt-2 list-inside list-disc space-y-1">
            <li>All your journeys and updates will be permanently deleted</li>
            <li>Your profile and all personal data will be removed</li>
            <li>You will lose access to your account and all its content</li>
            <li>This action cannot be undone</li>
          </ul>
        </div>
      </CardContent>

      <CardFooter className="border-t px-6 py-4">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button variant="destructive" className="text-white">
              <Trash2 className="mr-2 h-4 w-4" />
              Delete Account
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                Are you absolutely sure?
              </DialogTitle>
              <DialogDescription>
                This action cannot be undone. This will permanently delete your account and all
                associated data.
              </DialogDescription>
            </DialogHeader>

            <div className="py-4">
              <p className="text-sm font-medium">
                Type <span className="font-mono font-bold text-destructive">delete</span> to confirm
              </p>
              <Input
                placeholder='Type "delete"'
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                className="mt-2"
                disabled={loading}
              />
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)} disabled={loading}>
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={confirmText.trim().toLowerCase() !== "delete" || loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  "Delete Account"
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardFooter>
    </Card>
  );
}
