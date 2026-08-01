import { useState, useEffect, useCallback } from "react";
import { journeyService } from "@/services/auth";
import { toast } from "sonner";

export function useTags(journeyId, updateId, initialTags = []) {
  const [tags, setTags] = useState(initialTags);
  const [loading, setLoading] = useState(false);
  const [trending, setTrending] = useState([]);
  const [inputValue, setInputValue] = useState("");

  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const response = await journeyService.getTrendingTags();
        setTrending(response.data || []);
      } catch {
        // ignore
      }
    };
    fetchTrending();
  }, []);

  const addTag = useCallback(
    async (tagName) => {
      if (!tagName.trim()) return false;
      if (tags.some((t) => t.name === tagName)) {
        toast.warning("Tag already added");
        return false;
      }
      setLoading(true);
      try {
        const newTags = [...tags, { name: tagName }];
        const response = await journeyService.updateUpdateTags(
          journeyId,
          updateId,
          newTags.map((t) => t.name),
        );
        setTags(response.data || []);
        toast.success("Tag added");
        setInputValue("");
        return true;
      } catch {
        toast.error("Failed to add tag");
        return false;
      } finally {
        setLoading(false);
      }
    },
    [journeyId, updateId, tags],
  );

  const removeTag = useCallback(
    async (tagName) => {
      const newTags = tags.filter((t) => t.name !== tagName);
      setLoading(true);
      try {
        const response = await journeyService.updateUpdateTags(
          journeyId,
          updateId,
          newTags.map((t) => t.name),
        );
        setTags(response.data || []);
        toast.success("Tag removed");
        return true;
      } catch {
        toast.error("Failed to remove tag");
        return false;
      } finally {
        setLoading(false);
      }
    },
    [journeyId, updateId, tags],
  );

  return {
    tags,
    setTags,
    trending,
    loading,
    inputValue,
    setInputValue,
    addTag,
    removeTag,
  };
}
