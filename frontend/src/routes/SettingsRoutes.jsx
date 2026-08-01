import { Route } from "react-router-dom";

import Settings from "@/pages/Settings";
import ProfileSettings from "@/pages/settings/ProfileSettings";
import PreferencesSettings from "@/pages/settings/PreferenceSettings";
import DeleteAccount from "@/pages/settings/DeleteAccount";
import ClearData from "@/pages/settings/ClearData";

export default function SettingsRoutes() {
  return (
    <Route path="/settings" element={<Settings />}>
      <Route index element={<ProfileSettings />} />
      <Route path="profile" element={<ProfileSettings />} />
      <Route path="preferences" element={<PreferencesSettings />} />
      <Route path="clear-data" element={<ClearData />} />
      <Route path="delete-account" element={<DeleteAccount />} />
    </Route>
  );
}
