import { Route } from "react-router-dom";

import FeedLatest from "@/pages/feed/Latest";
import FeedFollowing from "@/pages/feed/Following";
import FeedTrending from "@/pages/feed/Trending";
import FeedHelpNeeded from "@/pages/feed/HelpNeeded";

export default function FeedRoutes() {
  return (
    <>
      <Route path="/feed/latest" element={<FeedLatest />} />
      <Route path="/feed/following" element={<FeedFollowing />} />
      <Route path="/feed/trending" element={<FeedTrending />} />
      <Route path="/feed/help-needed" element={<FeedHelpNeeded />} />
    </>
  );
}
