import { useState } from "react";
import { Reply, Check, ChevronDown, ChevronUp } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export function CommentItem({
  comment,
  currentUser,
  isOwner,
  helpNeeded,
  acceptedSolution,
  onAcceptSolution,
  onDeleteComment,
  onUpdateComment,
  onAddReply,
  onUpdateReply,
  onDeleteReply,
}) {
  const [editingComment, setEditingComment] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [showReplies, setShowReplies] = useState(false);
  const [replyInput, setReplyInput] = useState("");
  const [replyVisible, setReplyVisible] = useState(false);
  const [editingReplyId, setEditingReplyId] = useState(null);
  const [editReplyContent, setEditReplyContent] = useState("");
  const isCommentAuthor = currentUser?.id === comment.user?.id;
  const replies = comment.replies || [];

  const handleSaveComment = async () => {
    if (await onUpdateComment(comment.id, editContent)) {
      setEditingComment(false);
    }
  };

  const handleDeleteComment = async () => {
    if (await onDeleteComment(comment.id)) {
      // no extra action
    }
  };

  const handleReplySubmit = async () => {
    if (!replyInput.trim()) return;
    if (await onAddReply(comment.id, replyInput)) {
      setReplyInput("");
      setReplyVisible(false);
    }
  };

  const handleSaveReply = async (replyId, content) => {
    if (await onUpdateReply(replyId, content)) {
      setEditingReplyId(null);
      setEditReplyContent("");
    }
  };

  const handleDeleteReply = async (replyId) => {
    if (await onDeleteReply(replyId)) {
      // no extra action
    }
  };

  return (
    <Card>
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start gap-3">
          <Avatar className="h-8 w-8">
            <AvatarImage src={comment.user?.avatar_url} alt={comment.user?.username} />
            <AvatarFallback>
              {comment.user?.username?.charAt(0)?.toUpperCase() || "U"}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-medium text-sm">{comment.user?.username}</span>
              <span className="text-xs text-muted-foreground">
                {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
              </span>
              {acceptedSolution?.comment?.id === comment.id && (
                <Badge className="bg-emerald-100 text-emerald-700 text-[10px]">Solution</Badge>
              )}
            </div>
            {editingComment ? (
              <div className="mt-2">
                <Textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  className="min-h-15 text-sm"
                />
                <div className="flex gap-2 mt-2">
                  <Button size="sm" onClick={handleSaveComment}>
                    Save
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditingComment(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <p className="text-sm mt-1">{comment.content}</p>
            )}
            <div className="flex items-center gap-3 mt-1.5 text-xs">
              {isOwner && helpNeeded && !acceptedSolution && (
                <button
                  onClick={() => onAcceptSolution(comment.id)}
                  className="text-primary hover:underline flex items-center gap-1"
                >
                  <Check className="h-3 w-3" />
                  Accept as solution
                </button>
              )}
              {isCommentAuthor && !editingComment && (
                <>
                  <button
                    onClick={() => {
                      setEditingComment(true);
                      setEditContent(comment.content);
                    }}
                    className="text-muted-foreground hover:text-primary"
                  >
                    Edit
                  </button>
                  <button
                    onClick={handleDeleteComment}
                    className="text-muted-foreground hover:text-destructive"
                  >
                    Delete
                  </button>
                </>
              )}
              <button
                onClick={() => setReplyVisible(!replyVisible)}
                className="text-muted-foreground hover:text-primary flex items-center gap-1"
              >
                <Reply className="h-3 w-3" />
                Reply
              </button>
              {replies.length > 0 && (
                <button
                  onClick={() => setShowReplies(!showReplies)}
                  className="text-muted-foreground hover:text-primary flex items-center gap-1"
                >
                  {showReplies ? (
                    <>
                      <ChevronUp className="h-3 w-3" />
                      Hide replies
                    </>
                  ) : (
                    <>
                      <ChevronDown className="h-2 w-2" />
                      {replies.length} {replies.length === 1 ? "reply" : "replies"}
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>

        {replyVisible && (
          <div className="ml-10 mt-2 flex gap-2">
            <Input
              placeholder="Write a reply..."
              value={replyInput}
              onChange={(e) => setReplyInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  handleReplySubmit();
                }
              }}
            />
            <Button size="sm" onClick={handleReplySubmit}>
              Reply
            </Button>
          </div>
        )}

        {showReplies && replies.length > 0 && (
          <div className="ml-10 space-y-3 mt-3 border-l-2 pl-4">
            {replies.map((reply) => {
              const isReplyAuthor = currentUser?.id === reply.user?.id;
              return (
                <div key={reply.id} className="flex items-start gap-3">
                  <Avatar className="h-6 w-6">
                    <AvatarImage src={reply.user?.avatar_url} alt={reply.user?.username} />
                    <AvatarFallback>
                      {reply.user?.username?.charAt(0)?.toUpperCase() || "U"}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-sm">{reply.user?.username}</span>
                      <span className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(reply.created_at), { addSuffix: true })}
                      </span>
                    </div>
                    {editingReplyId === reply.id ? (
                      <div className="mt-1">
                        <Textarea
                          value={editReplyContent}
                          onChange={(e) => setEditReplyContent(e.target.value)}
                          className="min-h-12.5 text-sm"
                        />
                        <div className="flex gap-2 mt-1">
                          <Button
                            size="sm"
                            onClick={() => handleSaveReply(reply.id, editReplyContent)}
                          >
                            Save
                          </Button>
                          <Button size="sm" variant="ghost" onClick={() => setEditingReplyId(null)}>
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <p className="text-sm">{reply.content}</p>
                    )}
                    {isReplyAuthor && !editingReplyId && (
                      <div className="flex gap-2 mt-1 text-xs">
                        <button
                          onClick={() => {
                            setEditingReplyId(reply.id);
                            setEditReplyContent(reply.content);
                          }}
                          className="text-muted-foreground hover:text-primary"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteReply(reply.id)}
                          className="text-muted-foreground hover:text-destructive"
                        >
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
