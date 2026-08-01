import { Route } from "react-router-dom";

import Dashboard from "@/pages/dashboard/Dashboard";
import Notifications from "@/pages/dashboard/Notifications";
import Profile from "@/pages/profile/Profile";
import PublicProfile from "@/pages/profile/PublicProfile";

export default function DashboardRoutes() {
  return (
    <>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/notifications" element={<Notifications />} />
      <Route path="/account" element={<Profile />} />
      <Route path="/profile/:username" element={<PublicProfile />} />
    </>
  );
}
