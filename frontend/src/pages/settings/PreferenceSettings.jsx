import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

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
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

export default function PreferencesSettings() {
  const [loading, setLoading] = useState(false);
  const [preferences, setPreferences] = useState({
    show_email: false,
    show_full_name: true,
    email_notifications: true,
    show_activity_status: true,
    allow_direct_messages: true,
  });

  useEffect(() => {
    const fetchPreferences = async () => {
      try {
        const response = await authService.getPreferences();
        setPreferences(response.data);
        // eslint-disable-next-line no-unused-vars
      } catch (err) {
        toast.error("Failed to load preferences");
      }
    };
    fetchPreferences();
  }, []);

  const handleToggle = (key) => {
    setPreferences((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await authService.updatePreferences(preferences);
      toast.success("Preferences updated successfully");
      // eslint-disable-next-line no-unused-vars
    } catch (err) {
      toast.error("Failed to update preferences");
    } finally {
      setLoading(false);
    }
  };

  const preferenceGroups = [
    {
      title: "Privacy",
      description: "Control who can see your information",
      items: [
        {
          key: "show_email",
          label: "Show email on profile",
          description: "Your email will be visible to other users",
        },
        {
          key: "show_full_name",
          label: "Show full name",
          description: "Your first and last name will be visible",
        },
        {
          key: "show_activity_status",
          label: "Show activity status",
          description: "Let others know when you're online",
        },
      ],
    },
    {
      title: "Notifications (Coming Soon)",
      description: "Manage your notification preferences",
      items: [
        {
          key: "email_notifications",
          label: "Email notifications",
          description: "Receive email updates about activity",
        },
        {
          key: "allow_direct_messages",
          label: "Allow direct messages",
          description: "Allow other users to send you messages",
        },
      ],
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Preferences</CardTitle>
        <CardDescription>Manage your privacy and notification settings</CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {preferenceGroups.map((group, idx) => (
          <div key={group.title}>
            {idx > 0 && <Separator className="my-6" />}
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium">{group.title}</h3>
                <p className="text-sm text-muted-foreground">{group.description}</p>
              </div>
              <div className="space-y-4">
                {group.items.map((item) => (
                  <div key={item.key} className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <Label htmlFor={item.key} className="text-sm font-medium">
                        {item.label}
                      </Label>
                      <p className="text-sm text-muted-foreground">{item.description}</p>
                    </div>
                    <Switch
                      id={item.key}
                      checked={preferences[item.key]}
                      onCheckedChange={() => handleToggle(item.key)}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </CardContent>

      <CardFooter className="border-t px-6 py-4">
        <Button onClick={handleSave} disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            "Save Preferences"
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}
