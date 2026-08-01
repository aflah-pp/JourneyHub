import { useEffect, useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

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
import { Field, FieldDescription, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const profileSchema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z.string().email("Invalid email address").optional(),
  bio: z.string().max(250, "Bio must be at most 250 characters").optional(),
  location: z.string().max(100, "Location must be at most 100 characters").optional(),
  website: z.string().url("Invalid URL").optional().or(z.literal("")),
  what_i_do: z.string().max(100, "Must be at most 100 characters").optional(),
});

export default function ProfileSettings() {
  const { user, setUser } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(null);

  const { control, handleSubmit, reset } = useForm({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      bio: "",
      location: "",
      website: "",
      what_i_do: "",
    },
  });

  useEffect(() => {
    if (user) {
      reset({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        email: user.email || "",
        bio: user.profile?.bio || "",
        location: user.profile?.location || "",
        website: user.profile?.website || "",
        what_i_do: user.profile?.what_i_do || "",
      });
      if (user.profile?.avatar_url) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setAvatarPreview(user.profile.avatar_url);
      }
    }
  }, [user, reset]);

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAvatarFile(file);
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      const formData = new FormData();
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
          formData.append(key, value);
        }
      });
      if (avatarFile) {
        formData.append("avatar", avatarFile);
      }

      const response = await authService.updateProfile(formData);
      const updatedUser = response.data;

      setUser(updatedUser);

      toast.success(response.message || "Profile updated successfully");
    } catch (err) {
      console.error("Profile update error:", err);
      const errorMessage = err.response?.data?.message || err.message || "Failed to update profile";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const initials = user?.username?.[0]?.toUpperCase() || "U";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profile Settings</CardTitle>
        <CardDescription>Update your personal information and public profile</CardDescription>
      </CardHeader>

      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-6">
          <div className="flex items-center gap-6">
            <Avatar className="h-20 w-20 border-2 border-border">
              <AvatarImage src={avatarPreview} alt="Avatar" />
              <AvatarFallback className="text-2xl">{initials}</AvatarFallback>
            </Avatar>
            <div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => document.getElementById("avatar-upload").click()}
                type="button"
              >
                Change Avatar
              </Button>
              <input
                id="avatar-upload"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleAvatarChange}
              />
              <p className="mt-1 text-xs text-muted-foreground">PNG, JPG, WebP up to 2MB</p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field>
              <FieldLabel htmlFor="first_name">First Name</FieldLabel>
              <Controller
                name="first_name"
                control={control}
                render={({ field }) => (
                  <Input id="first_name" placeholder="John" {...field} disabled={loading} />
                )}
              />
              {control._formState.errors.first_name && (
                <p className="text-sm text-red-500 mt-1">
                  {control._formState.errors.first_name.message}
                </p>
              )}
            </Field>

            <Field>
              <FieldLabel htmlFor="last_name">Last Name</FieldLabel>
              <Controller
                name="last_name"
                control={control}
                render={({ field }) => (
                  <Input id="last_name" placeholder="Doe" {...field} disabled={loading} />
                )}
              />
              {control._formState.errors.last_name && (
                <p className="text-sm text-red-500 mt-1">
                  {control._formState.errors.last_name.message}
                </p>
              )}
            </Field>
          </div>

          <Field>
            <FieldLabel htmlFor="email">Email</FieldLabel>
            <Controller
              name="email"
              control={control}
              render={({ field }) => (
                <Input
                  id="email"
                  type="email"
                  placeholder="john@example.com"
                  {...field}
                  disabled={loading}
                />
              )}
            />
            {control._formState.errors.email && (
              <p className="text-sm text-red-500 mt-1">{control._formState.errors.email.message}</p>
            )}
          </Field>

          <Field>
            <FieldLabel htmlFor="bio">Bio</FieldLabel>
            <Controller
              name="bio"
              control={control}
              render={({ field }) => (
                <Textarea
                  id="bio"
                  placeholder="Tell us about yourself..."
                  className="resize-none"
                  {...field}
                  disabled={loading}
                />
              )}
            />
            <FieldDescription>Brief description for your profile</FieldDescription>
            {control._formState.errors.bio && (
              <p className="text-sm text-red-500 mt-1">{control._formState.errors.bio.message}</p>
            )}
          </Field>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field>
              <FieldLabel htmlFor="location">Location</FieldLabel>
              <Controller
                name="location"
                control={control}
                render={({ field }) => (
                  <Input
                    id="location"
                    placeholder="San Francisco, CA"
                    {...field}
                    disabled={loading}
                  />
                )}
              />
              {control._formState.errors.location && (
                <p className="text-sm text-red-500 mt-1">
                  {control._formState.errors.location.message}
                </p>
              )}
            </Field>

            <Field>
              <FieldLabel htmlFor="website">Website</FieldLabel>
              <Controller
                name="website"
                control={control}
                render={({ field }) => (
                  <Input
                    id="website"
                    placeholder="https://example.com"
                    {...field}
                    disabled={loading}
                  />
                )}
              />
              {control._formState.errors.website && (
                <p className="text-sm text-red-500 mt-1">
                  {control._formState.errors.website.message}
                </p>
              )}
            </Field>
          </div>

          <Field>
            <FieldLabel htmlFor="what_i_do">What I do</FieldLabel>
            <Controller
              name="what_i_do"
              control={control}
              render={({ field }) => (
                <Input
                  id="what_i_do"
                  placeholder="Building full-stack applications"
                  {...field}
                  disabled={loading}
                />
              )}
            />
            <FieldDescription>Your profession or main focus</FieldDescription>
            {control._formState.errors.what_i_do && (
              <p className="text-sm text-red-500 mt-1">
                {control._formState.errors.what_i_do.message}
              </p>
            )}
          </Field>
        </CardContent>

        <CardFooter className="border-t px-6 py-4">
          <Button type="submit" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              "Save Changes"
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
