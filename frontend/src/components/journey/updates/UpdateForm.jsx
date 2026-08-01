import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2, Upload, Trash2, X, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Field, FieldLabel } from "@/components/ui/field";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { journeyService } from "@/services/auth";

const VISIBILITY_OPTIONS = [
  { value: "PUBLIC", label: "Public" },
  { value: "FOLLOWERS", label: "Followers Only" },
  { value: "PRIVATE", label: "Private" },
];

const MILESTONE_OPTIONS = [
  { value: "NONE", label: "None" },
  { value: "MILESTONE", label: "Milestone" },
  { value: "COMPLETED", label: "Completed" },
];

const updateSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  progress_percentage: z.number().min(0).max(100, "Progress must be between 0 and 100"),
  milestone_status: z.string().min(1, "Milestone status is required"),
  help_needed: z.boolean().default(false),
  visibility: z.string().optional(),
});

export function UpdateForm({ mode, initialData = null, journeyId, updateId = null }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState([]);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [imageFiles, setImageFiles] = useState([]);
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState("");

  const isEdit = mode === "edit";

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
    reset,
  } = useForm({
    resolver: zodResolver(updateSchema),
    defaultValues: {
      title: "",
      description: "",
      progress_percentage: 0,
      milestone_status: "NONE",
      help_needed: false,
      visibility: "",
    },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        title: initialData.title || "",
        description: initialData.description || "",
        progress_percentage: initialData.progress_percentage || 0,
        milestone_status: initialData.milestone_status || "NONE",
        help_needed: initialData.help_needed || false,
        visibility: initialData.visibility || "",
      });
      if (initialData.images && initialData.images.length > 0) {
        setImages(initialData.images);
      }
      if (initialData.tags) {
        setTags(initialData.tags.map((tag) => tag.name || tag));
      }
    }
  }, [initialData, reset]);

  const handleAddTag = () => {
    const trimmed = tagInput.trim();
    if (!trimmed) return;
    if (tags.includes(trimmed)) {
      toast.warning("Tag already added");
      return;
    }
    if (tags.length >= 5) {
      toast.warning("Maximum 5 tags allowed");
      return;
    }
    setTags((prev) => [...prev, trimmed]);
    setTagInput("");
  };

  const handleRemoveTag = (tagToRemove) => {
    setTags((prev) => prev.filter((tag) => tag !== tagToRemove));
  };

  const handleTagKeyDown = (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleImageUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploadingImage(true);
    try {
      const file = files[0];

      if (isEdit && updateId) {
        const response = await journeyService.addUpdateImage(updateId, file, images.length);
        setImages((prev) => [...prev, response.data]);
        toast.success("Image uploaded");
      } else {
        setImageFiles((prev) => [...prev, file]);
        const previewUrl = URL.createObjectURL(file);
        setImages((prev) => [...prev, { cloudinary_url: previewUrl, id: `temp-${Date.now()}` }]);
        toast.success("Image added (will be uploaded on save)");
      }
    } catch {
      toast.error("Failed to upload image");
    } finally {
      setUploadingImage(false);
      e.target.value = "";
    }
  };

  const removeImage = async (imageId) => {
    if (isEdit && updateId && !imageId.startsWith("temp-")) {
      try {
        await journeyService.deleteUpdateImage(updateId, imageId);
        setImages((prev) => prev.filter((img) => img.id !== imageId));
        toast.success("Image removed");
      } catch {
        toast.error("Failed to remove image");
      }
    } else {
      setImages((prev) => prev.filter((img) => img.id !== imageId));
      const indexToRemove = images.findIndex((img) => img.id === imageId);
      if (indexToRemove !== -1) {
        setImageFiles((prev) => prev.filter((_, idx) => idx !== indexToRemove));
      }
    }
  };

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      const payload = {
        title: data.title,
        description: data.description,
        progress_percentage: data.progress_percentage,
        milestone_status: data.milestone_status,
        help_needed: data.help_needed,
        visibility: data.visibility || undefined,
      };

      let response;
      if (isEdit) {
        response = await journeyService.updateUpdate(journeyId, updateId, payload);
        if (tags.length > 0) {
          await journeyService.updateUpdateTags(journeyId, updateId, tags);
        }
      } else {
        response = await journeyService.createUpdate(journeyId, payload);
        const newUpdateId = response.data.id;

        if (tags.length > 0) {
          await journeyService.updateUpdateTags(journeyId, newUpdateId, tags);
        }

        if (imageFiles.length > 0) {
          for (let i = 0; i < imageFiles.length; i++) {
            await journeyService.addUpdateImage(newUpdateId, imageFiles[i], i);
          }
        }
      }

      toast.success(isEdit ? "Update saved!" : "Update created!");
      navigate(`/journeys/${journeyId}`);
    } catch (err) {
      toast.error(err.response?.data?.message || "Operation failed");
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/incompatible-library
  const watchedHelpNeeded = watch("help_needed");
  const watchedProgress = watch("progress_percentage") || 0;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Card>
        <CardContent className="p-6 space-y-6">
          {/* Title */}
          <Field>
            <FieldLabel htmlFor="title">Title</FieldLabel>
            <Input
              id="title"
              placeholder="Enter update title"
              {...register("title")}
              disabled={loading}
            />
            {errors.title && <p className="text-sm text-red-500 mt-1">{errors.title.message}</p>}
          </Field>

          {/* Description */}
          <Field>
            <FieldLabel htmlFor="description">Description</FieldLabel>
            <Textarea
              id="description"
              placeholder="Describe your progress..."
              className="resize-none min-h-30"
              {...register("description")}
              disabled={loading}
            />
            {errors.description && (
              <p className="text-sm text-red-500 mt-1">{errors.description.message}</p>
            )}
          </Field>

          {/* Progress Percentage */}
          <Field>
            <FieldLabel htmlFor="progress_percentage">Progress</FieldLabel>
            <div className="flex items-center gap-4">
              <Input
                id="progress_percentage"
                type="number"
                min="0"
                max="100"
                className="w-24"
                {...register("progress_percentage", { valueAsNumber: true })}
                disabled={loading}
              />
              <span className="text-sm text-muted-foreground">%</span>
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                value={watchedProgress}
                onChange={(e) => setValue("progress_percentage", parseInt(e.target.value))}
                className="flex-1 h-2 appearance-none bg-muted rounded-lg"
                disabled={loading}
              />
            </div>
            {errors.progress_percentage && (
              <p className="text-sm text-red-500 mt-1">{errors.progress_percentage.message}</p>
            )}
          </Field>

          {/* Milestone Status */}
          <Field>
            <FieldLabel htmlFor="milestone_status">Milestone Status</FieldLabel>
            <Select
              onValueChange={(value) => setValue("milestone_status", value)}
              defaultValue={initialData?.milestone_status || "NONE"}
              disabled={loading}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select milestone status" />
              </SelectTrigger>
              <SelectContent>
                {MILESTONE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.milestone_status && (
              <p className="text-sm text-red-500 mt-1">{errors.milestone_status.message}</p>
            )}
          </Field>

          {/* Help Needed Toggle */}
          <Field>
            <div className="flex items-start gap-3">
              <Checkbox
                id="help_needed"
                checked={watchedHelpNeeded}
                onCheckedChange={(checked) => setValue("help_needed", checked)}
                disabled={loading}
                className="mt-0.5"
              />
              <div className="space-y-0.5">
                <Label htmlFor="help_needed" className="text-sm font-medium cursor-pointer">
                  Help needed?
                </Label>
                <p className="text-xs text-muted-foreground">
                  Mark if you need community assistance
                </p>
                {errors.help_needed && (
                  <p className="text-sm text-red-500">{errors.help_needed.message}</p>
                )}
              </div>
            </div>
          </Field>

          {/* Visibility (optional) */}
          <Field>
            <FieldLabel htmlFor="visibility">Visibility (Optional)</FieldLabel>
            <Select
              onValueChange={(value) => setValue("visibility", value)}
              defaultValue={initialData?.visibility || ""}
              disabled={loading}
            >
              <SelectTrigger>
                <SelectValue placeholder="Leave empty to inherit journey visibility" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Inherit</SelectItem>
                {VISIBILITY_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.visibility && (
              <p className="text-sm text-red-500 mt-1">{errors.visibility.message}</p>
            )}
          </Field>

          {/* Tags */}
          <Field>
            <FieldLabel>Tags</FieldLabel>
            <div className="mt-2 space-y-3">
              <div className="flex items-center gap-2">
                <Input
                  placeholder="Add tag (max 5)"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleTagKeyDown}
                  disabled={loading}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAddTag}
                  disabled={loading || tags.length >= 5}
                  className="shrink-0"
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>

              {tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <Badge
                      key={tag}
                      variant="secondary"
                      className="flex items-center gap-1 px-3 py-1"
                    >
                      #{tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="hover:text-destructive transition-colors"
                        disabled={loading}
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
              <p className="text-xs text-muted-foreground">
                Press Enter or comma to add a tag. Max 5 tags.
              </p>
            </div>
          </Field>

          {/* Images */}
          <Field>
            <FieldLabel>Images</FieldLabel>
            <div className="mt-2 space-y-3">
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => document.getElementById("image-upload").click()}
                  disabled={loading || uploadingImage}
                >
                  {uploadingImage ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Upload className="h-4 w-4 mr-2" />
                  )}
                  Upload Image
                </Button>
                <input
                  id="image-upload"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleImageUpload}
                  disabled={loading || uploadingImage}
                />
                <span className="text-sm text-muted-foreground">PNG, JPG, WebP up to 5MB</span>
              </div>

              {images.length > 0 && (
                <div className="grid grid-cols-3 gap-3">
                  {images.map((img) => (
                    <div
                      key={img.id}
                      className="relative group aspect-square rounded-lg overflow-hidden border bg-muted"
                    >
                      <img
                        src={img.cloudinary_url || img.image}
                        alt="Update"
                        className="w-full h-full object-cover"
                      />
                      <Button
                        type="button"
                        variant="destructive"
                        size="icon"
                        className="absolute top-1 right-1 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => removeImage(img.id)}
                        disabled={loading}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Field>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={() => navigate(-1)} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading} className="gap-1.5">
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              {isEdit ? "Saving..." : "Creating..."}
            </>
          ) : isEdit ? (
            "Save Update"
          ) : (
            "Create Update"
          )}
        </Button>
      </div>
    </form>
  );
}
