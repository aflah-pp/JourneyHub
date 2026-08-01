import { Route } from "react-router-dom";

import Explore from "@/pages/explore/UserExplore";
import ExploreJourneys from "@/pages/explore/JourneyExplore";
import ExploreTags from "@/pages/explore/TagExplore";
import TagDetail from "@/pages/Tagdetail";

export default function ExploreRoutes() {
  return (
    <>
      <Route path="/explore/users" element={<Explore />} />
      <Route path="/explore/journeys" element={<ExploreJourneys />} />
      <Route path="/explore/trending-tags" element={<ExploreTags />} />
      <Route path="/explore/tags/:slug" element={<TagDetail />} />
    </>
  );
}
