/* eslint-disable react-hooks/incompatible-library */
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2, Send, Star } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { feedbackService } from "@/services/auth";

const feedbackSchema = z.object({
  feedback_type: z.string().min(1, "Please select a feedback type"),
  subject: z.string().min(3, "Subject must be at least 3 characters"),
  message: z.string().min(10, "Message must be at least 10 characters"),
  rating: z.number().min(1).max(5).optional().nullable(),
  is_anonymous: z.boolean().default(false),
});

export default function Feedback() {
  const [loading, setLoading] = useState(false);
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);

  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(feedbackSchema),
    defaultValues: {
      feedback_type: "",
      subject: "",
      message: "",
      rating: null,
      is_anonymous: false,
    },
  });

  const onSubmit = async (data) => {
    setLoading(true);

    try {
      await feedbackService.submitFeedback(data);
      toast.success("Thank you for your feedback!");
      navigate("/dashboard");
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to submit feedback");
    } finally {
      setLoading(false);
    }
  };

  const handleRatingClick = (value) => {
    setRating(value);
    setValue("rating", value);
  };

  return (
    <div className="flex h-full items-center justify-center">
      <Card className="flex h-full max-h-full w-full max-w-3xl flex-col overflow-hidden rounded-2xl shadow-sm">
        <CardHeader className="border-b pb-5">
          <CardTitle className="flex items-center gap-2 text-2xl">
            <Send className="h-6 w-6 text-primary" />
            Share Feedback
          </CardTitle>

          <CardDescription>
            Help us improve JourneyHub by sharing bugs, suggestions, feature requests, or general
            feedback.
          </CardDescription>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <Field>
              <FieldLabel htmlFor="feedback_type">Feedback Type</FieldLabel>

              <Select
                defaultValue={watch("feedback_type")}
                onValueChange={(value) => setValue("feedback_type", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select feedback type..." />
                </SelectTrigger>

                <SelectContent>
                  <SelectItem value="BUG">🐛 Bug Report</SelectItem>

                  <SelectItem value="FEATURE">💡 Feature Request</SelectItem>

                  <SelectItem value="IMPROVEMENT">⚡ Improvement</SelectItem>

                  <SelectItem value="GENERAL">💬 General Feedback</SelectItem>

                  <SelectItem value="OTHER">📝 Other</SelectItem>
                </SelectContent>
              </Select>

              {errors.feedback_type && (
                <p className="mt-1 text-sm text-destructive">{errors.feedback_type.message}</p>
              )}
            </Field>

            <Field>
              <FieldLabel htmlFor="subject">Subject</FieldLabel>

              <Input
                id="subject"
                placeholder="Brief summary..."
                disabled={loading}
                {...register("subject")}
              />

              {errors.subject && (
                <p className="mt-1 text-sm text-destructive">{errors.subject.message}</p>
              )}
            </Field>

            <Field>
              <FieldLabel htmlFor="message">Message</FieldLabel>

              <Textarea
                id="message"
                placeholder="Describe your feedback in detail..."
                className="min-h-40 resize-none"
                disabled={loading}
                {...register("message")}
              />

              {errors.message && (
                <p className="mt-1 text-sm text-destructive">{errors.message.message}</p>
              )}
            </Field>

            <Field>
              <FieldLabel>Rating</FieldLabel>

              <div className="flex items-center gap-2">
                {[1, 2, 3, 4, 5].map((value) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => handleRatingClick(value)}
                    onMouseEnter={() => setHoveredRating(value)}
                    onMouseLeave={() => setHoveredRating(0)}
                    className="transition-transform hover:scale-110"
                  >
                    <Star
                      className={`h-8 w-8 transition-colors ${
                        value <= (hoveredRating || rating)
                          ? "fill-yellow-400 text-yellow-400"
                          : "text-muted-foreground/30"
                      }`}
                    />
                  </button>
                ))}

                <span className="ml-3 text-sm text-muted-foreground">
                  {rating > 0 ? `${rating} / 5` : "Optional"}
                </span>
              </div>
            </Field>

            <div className="flex items-center justify-between rounded-xl border bg-muted/30 px-4 py-3">
              <div>
                <label htmlFor="is_anonymous" className="cursor-pointer font-medium">
                  Submit anonymously
                </label>

                <p className="mt-1 text-sm text-muted-foreground">
                  Your identity will remain hidden from moderators and other users.
                </p>
              </div>

              <input
                id="is_anonymous"
                type="checkbox"
                {...register("is_anonymous")}
                className="h-5 w-5 shrink-0 cursor-pointer rounded"
              />
            </div>

            <Button type="submit" disabled={loading} size="lg" className="w-full">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Submit Feedback
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
