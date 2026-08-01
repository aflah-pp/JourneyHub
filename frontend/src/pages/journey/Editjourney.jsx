import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { journeyService } from "@/services/auth";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { JourneyForm } from "@/components/journey/JourneyForm";

export default function EditJourney() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [journey, setJourney] = useState(null);

  useEffect(() => {
    const fetchJourney = async () => {
      try {
        const response = await journeyService.getJourneyDetail(id);
        let data = response.data;
        if (
          data &&
          typeof data === "object" &&
          data.results &&
          Array.isArray(data.results) &&
          data.results.length > 0
        ) {
          data = data.results[0];
        }
        setJourney(data);
      } catch {
        toast.error("Failed to load journey");
        navigate("/journeys");
      } finally {
        setLoading(false);
      }
    };
    fetchJourney();
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!journey) {
    return (
      <div className="text-center py-16">
        <p className="text-muted-foreground">Journey not found.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold tracking-tight mb-6">Edit Journey</h1>
      <JourneyForm mode="edit" initialData={journey} journeyId={id} />
    </div>
  );
}
