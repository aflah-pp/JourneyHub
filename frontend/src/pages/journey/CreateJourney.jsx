import { JourneyForm } from "@/components/journey/JourneyForm";

export default function CreateJourney() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold tracking-tight mb-6">Create New Journey</h1>
      <JourneyForm mode="create" />
    </div>
  );
}
