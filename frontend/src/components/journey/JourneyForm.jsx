import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2, X, Image as ImageIcon } from "lucide-react";
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
import { journeyService } from "@/services/auth";

const CATEGORIES = [
  { value: "SOFTWARE", label: "Software" },
  { value: "STARTUP", label: "Startup" },
  { value: "SKILL", label: "Skill" },
  { value: "RESEARCH", label: "Research" },
  { value: "BOOK", label: "Book" },
  { value: "ART", label: "Art" },
  { value: "FITNESS", label: "Fitness" },
  { value: "DIY", label: "DIY" },
  { value: "CONTENT", label: "Content" },
  { value: "CHALLENGE", label: "Challenge" },
  { value: "OTHER", label: "Other" },
];

const VISIBILITY_OPTIONS = [
  { value: "PUBLIC", label: "Public" },
  { value: "FOLLOWERS", label: "Followers Only" },
  { value: "PRIVATE", label: "Private" },
];

const STATUS_OPTIONS = [
  { value: "ACTIVE", label: "Active" },
  { value: "PAUSED", label: "Paused" },
  { value: "COMPLETED", label: "Completed" },
  { value: "ABANDONED", label: "Abandoned" },
];

const baseSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  category: z.string().min(1, "Category is required"),
  description: z.string().optional(),
  visibility: z.string().min(1, "Visibility is required"),
});

const createSchema = baseSchema.extend({
  cover_image: z.any().optional(),
});

const updateSchema = baseSchema.extend({
  status: z.string().min(1, "Status is required"),
});

export function JourneyForm({ mode, initialData = null, journeyId = null }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [coverPreview, setCoverPreview] = useState(null);
  const [coverFile, setCoverFile] = useState(null);

  const isEdit = mode === "edit";
  const schema = isEdit ? updateSchema : createSchema;

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
    reset,
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: isEdit
      ? {
          title: "",
          category: "",
          description: "",
          visibility: "",
          status: "",
        }
      : {
          title: "",
          category: "",
          description: "",
          visibility: "PUBLIC",
        },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        title: initialData.title || "",
        category: initialData.category || "",
        description: initialData.description || "",
        visibility: initialData.visibility || "PUBLIC",
        status: initialData.status || "ACTIVE",
      });
      if (initialData.cover_image_url) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setCoverPreview(initialData.cover_image_url);
      }
    }
  }, [initialData, reset]);

  const handleCoverChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCoverFile(file);
      setCoverPreview(URL.createObjectURL(file));
    }
  };

  const removeCover = () => {
    setCoverFile(null);
    setCoverPreview(null);
  };

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      const formData = new FormData();
      Object.keys(data).forEach((key) => {
        if (data[key] !== undefined && data[key] !== null && data[key] !== "") {
          formData.append(key, data[key]);
        }
      });
      if (coverFile) {
        formData.append("cover_image", coverFile);
      }

      let response;
      if (isEdit) {
        response = await journeyService.updateJourney(journeyId, formData);
      } else {
        // eslint-disable-next-line no-unused-vars
        response = await journeyService.createJourney(formData);
      }

      toast.success(isEdit ? "Journey updated successfully!" : "Journey created successfully!");
      navigate("/journeys");
    } catch (err) {
      toast.error(
        err.response?.data?.message ||
          (isEdit ? "Failed to update journey" : "Failed to create journey"),
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Card>
        <CardContent className="p-6 space-y-6">
          {/* Title */}
          <Field>
            <FieldLabel htmlFor="title">Title</FieldLabel>
            <Input
              id="title"
              placeholder="Enter journey title"
              {...register("title")}
              disabled={loading}
            />
            {errors.title && <p className="text-sm text-red-500 mt-1">{errors.title.message}</p>}
          </Field>

          {/* Category */}
          <Field>
            <FieldLabel htmlFor="category">Category</FieldLabel>
            <Select
              onValueChange={(value) => setValue("category", value)}
              defaultValue={initialData?.category || ""}
              disabled={loading}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map((cat) => (
                  <SelectItem key={cat.value} value={cat.value}>
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.category && (
              <p className="text-sm text-red-500 mt-1">{errors.category.message}</p>
            )}
          </Field>

          {/* Description */}
          <Field>
            <FieldLabel htmlFor="description">Description</FieldLabel>
            <Textarea
              id="description"
              placeholder="Describe your journey..."
              className="resize-none min-h-30"
              {...register("description")}
              disabled={loading}
            />
            {errors.description && (
              <p className="text-sm text-red-500 mt-1">{errors.description.message}</p>
            )}
          </Field>

          {/* Visibility */}
          <Field>
            <FieldLabel htmlFor="visibility">Visibility</FieldLabel>
            <Select
              onValueChange={(value) => setValue("visibility", value)}
              defaultValue={initialData?.visibility || "PUBLIC"}
              disabled={loading}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select visibility" />
              </SelectTrigger>
              <SelectContent>
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

          {/* Status (only for edit) */}
          {isEdit && (
            <Field>
              <FieldLabel htmlFor="status">Status</FieldLabel>
              <Select
                onValueChange={(value) => setValue("status", value)}
                defaultValue={initialData?.status || "ACTIVE"}
                disabled={loading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  {STATUS_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.status && (
                <p className="text-sm text-red-500 mt-1">{errors.status.message}</p>
              )}
            </Field>
          )}

          {/* Cover Image (only for create) */}
          {!isEdit && (
            <Field>
              <FieldLabel htmlFor="cover_image">Cover Image (Optional)</FieldLabel>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-lg hover:border-primary/50 transition-colors">
                {coverPreview ? (
                  <div className="relative w-full">
                    <img
                      src={coverPreview}
                      alt="Cover preview"
                      className="max-h-48 mx-auto object-cover rounded-md"
                    />
                    <Button
                      type="button"
                      variant="destructive"
                      size="icon"
                      className="absolute top-2 right-2 h-8 w-8 rounded-full"
                      onClick={removeCover}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ) : (
                  <div className="text-center space-y-2">
                    <ImageIcon className="mx-auto h-12 w-12 text-muted-foreground/40" />
                    <div className="flex text-sm text-muted-foreground">
                      <label
                        htmlFor="cover-upload"
                        className="relative cursor-pointer rounded-md font-medium text-primary hover:text-primary/80"
                      >
                        <span>Upload a cover image</span>
                        <input
                          id="cover-upload"
                          type="file"
                          accept="image/*"
                          className="sr-only"
                          onChange={handleCoverChange}
                          disabled={loading}
                        />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-muted-foreground">PNG, JPG, WebP up to 5MB</p>
                  </div>
                )}
              </div>
              {errors.cover_image && (
                <p className="text-sm text-red-500 mt-1">{errors.cover_image.message}</p>
              )}
            </Field>
          )}
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
              {isEdit ? "Updating..." : "Creating..."}
            </>
          ) : isEdit ? (
            "Update Journey"
          ) : (
            "Create Journey"
          )}
        </Button>
      </div>
    </form>
  );
}
