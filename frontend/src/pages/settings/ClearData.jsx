import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Loader2, AlertTriangle, Trash2 } from "lucide-react";
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

export default function ClearData() {
  const navigate = useNavigate();
  const [confirmText, setConfirmText] = useState("");
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  const handleClearData = async () => {
    if (confirmText.trim().toLowerCase() !== "clear") {
      toast.error('Please type "clear" to confirm');
      return;
    }

    setLoading(true);
    try {
      await authService.clearUserData(confirmText.trim().toLowerCase());
      toast.success("All your data has been cleared successfully.");

      navigate("/dashboard");
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to clear data");
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
          Clear All Data
        </CardTitle>
        <CardDescription>
          Permanently delete all your journeys, updates, likes, comments, and saved items. Your
          account and profile will remain but will be empty.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="rounded-lg bg-destructive/10 p-4 text-sm text-destructive">
          <p className="font-medium">⚠️ What will be cleared:</p>
          <ul className="mt-2 list-inside list-disc space-y-1">
            <li>All your journeys and updates</li>
            <li>All your likes, comments, and replies</li>
            <li>All saved journeys and updates</li>
            <li>All notifications</li>
            <li>Your profile bio, location, website, and other details</li>
            <li>Your builder score and streak</li>
            <li>Your follow relationships</li>
          </ul>
          <p className="mt-2 font-medium">
            Your account will remain active and you can start fresh.
          </p>
        </div>
      </CardContent>

      <CardFooter className="border-t px-6 py-4">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button variant="destructive" className="text-white">
              <Trash2 className="mr-2 h-4 w-4" />
              Clear All Data
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                Are you absolutely sure?
              </DialogTitle>
              <DialogDescription>
                This action cannot be undone. All your data will be permanently cleared.
              </DialogDescription>
            </DialogHeader>

            <div className="py-4">
              <p className="text-sm font-medium">
                Type <span className="font-mono font-bold text-destructive">clear</span> to confirm
              </p>
              <Input
                placeholder='Type "clear"'
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
                onClick={handleClearData}
                disabled={confirmText.trim().toLowerCase() !== "clear" || loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Clearing...
                  </>
                ) : (
                  "Clear All Data"
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardFooter>
    </Card>
  );
}
