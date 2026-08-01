import { useParams, useNavigate } from "react-router-dom";
import { UpdateForm } from "@/components/journey/updates/UpdateForm";

export default function CreateUpdate() {
  const { journeyId } = useParams();
  const navigate = useNavigate();

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold tracking-tight mb-6">Create New Update</h1>
      <UpdateForm
        mode="create"
        journeyId={journeyId}
        onSuccess={() => navigate(`/journeys/${journeyId}`)}
      />
    </div>
  );
}
