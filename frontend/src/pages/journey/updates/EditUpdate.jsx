import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { journeyService } from "@/services/auth";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { UpdateForm } from "@/components/journey/updates/UpdateForm";

export default function EditUpdate() {
  const { journeyId, updateId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [updateData, setUpdateData] = useState(null);

  useEffect(() => {
    const fetchUpdate = async () => {
      try {
        const response = await journeyService.getUpdateDetail(journeyId, updateId);
        setUpdateData(response.data);
      } catch {
        toast.error("Failed to load update");
        navigate(`/journeys/${journeyId}`);
      } finally {
        setLoading(false);
      }
    };
    fetchUpdate();
  }, [journeyId, updateId, navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!updateData) {
    return (
      <div className="text-center py-16">
        <p className="text-muted-foreground">Update not found.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold tracking-tight mb-6">Edit Update</h1>
      <UpdateForm mode="edit" initialData={updateData} journeyId={journeyId} updateId={updateId} />
    </div>
  );
}
