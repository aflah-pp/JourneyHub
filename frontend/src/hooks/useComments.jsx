import { useState, useEffect, useCallback } from "react";
import { reactionService } from "@/services/auth";
import { toast } from "sonner";

export function useComments(updateId) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [cursor, setCursor] = useState(null);
  const [hasMore, setHasMore] = useState(false);
  const [newCommentContent, setNewCommentContent] = useState("");

  const fetchComments = useCallback(
    async (nextCursor = null) => {
      setLoading(true);
      try {
        const response = await reactionService.getComments(updateId, nextCursor);
        const results = response.data?.results || [];
        const next = response.data?.next_cursor || null;
        if (nextCursor) {
          setComments((prev) => [...prev, ...results]);
        } else {
          setComments(results);
        }
        setCursor(next);
        setHasMore(!!next);
      } catch {
        toast.error("Failed to load comments");
      } finally {
        setLoading(false);
      }
    },
    [updateId],
  );

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchComments();
  }, [fetchComments]);

  const addComment = useCallback(
    async (content) => {
      if (!content.trim()) return false;
      try {
        const response = await reactionService.createComment(updateId, content);
        const newComment = response.data;
        setComments((prev) => [newComment, ...prev]);
        setNewCommentContent("");
        return true;
      } catch {
        toast.error("Failed to add comment");
        return false;
      }
    },
    [updateId],
  );

  const editComment = useCallback(async (commentId, content) => {
    try {
      const response = await reactionService.updateComment(commentId, content);
      const updated = response.data;
      setComments((prev) =>
        prev.map((c) => (c.id === commentId ? { ...c, content: updated.content } : c)),
      );
      return true;
    } catch {
      toast.error("Failed to update comment");
      return false;
    }
  }, []);

  const deleteComment = useCallback(async (commentId) => {
    try {
      await reactionService.deleteComment(commentId);
      setComments((prev) => prev.filter((c) => c.id !== commentId));
      return true;
    } catch {
      toast.error("Failed to delete comment");
      return false;
    }
  }, []);

  const addReply = useCallback(async (commentId, content) => {
    try {
      const response = await reactionService.createReply(commentId, content);
      const newReply = response.data;
      setComments((prev) =>
        prev.map((c) => {
          if (c.id === commentId) {
            return { ...c, replies: [...(c.replies || []), newReply] };
          }
          return c;
        }),
      );
      return true;
    } catch {
      toast.error("Failed to add reply");
      return false;
    }
  }, []);

  const editReply = useCallback(async (replyId, content) => {
    try {
      const response = await reactionService.updateReply(replyId, content);
      const updated = response.data;
      setComments((prev) =>
        prev.map((c) => ({
          ...c,
          replies:
            c.replies?.map((r) => (r.id === replyId ? { ...r, content: updated.content } : r)) ||
            [],
        })),
      );
      return true;
    } catch {
      toast.error("Failed to update reply");
      return false;
    }
  }, []);

  const deleteReply = useCallback(async (replyId) => {
    try {
      await reactionService.deleteReply(replyId);
      setComments((prev) =>
        prev.map((c) => ({
          ...c,
          replies: c.replies?.filter((r) => r.id !== replyId) || [],
        })),
      );
      return true;
    } catch {
      toast.error("Failed to delete reply");
      return false;
    }
  }, []);

  return {
    comments,
    loading,
    hasMore,
    cursor,
    newCommentContent,
    setNewCommentContent,
    fetchComments,
    addComment,
    editComment,
    deleteComment,
    addReply,
    editReply,
    deleteReply,
  };
}
