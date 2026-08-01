import CreateJourney from "@/pages/journey/CreateJourney";
import EditJourney from "@/pages/journey/Editjourney";
import Journeys from "@/pages/journey/Journey";
import JourneyDetail from "@/pages/journey/JourneyDetail";
import CreateUpdate from "@/pages/journey/updates/CreateUpdate";
import EditUpdate from "@/pages/journey/updates/EditUpdate";
import UpdateDetail from "@/pages/journey/updates/UpdateDetail";
import { Route } from "react-router-dom";

export default function JourneyRoutes() {
  return (
    <>
      <Route path="/journeys" element={<Journeys />} />
      <Route path="/journeys/create" element={<CreateJourney />} />
      <Route path="/journeys/:id" element={<JourneyDetail />} />
      <Route path="/journeys/:id/edit" element={<EditJourney />} />
      <Route path="/journeys/:id/updates/create" element={<CreateUpdate />} />
      <Route path="/journeys/:journeyId/updates/:updateId" element={<UpdateDetail />} />
      <Route path="/journeys/:journeyId/updates/:updateId/edit" element={<EditUpdate />} />
    </>
  );
}
