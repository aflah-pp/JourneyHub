import { Route } from "react-router-dom";

import { ProtectedRoute } from "@/components/shared/ProtectedRoute";
import { AppLayout } from "@/components/layout/app-layout";

import DashboardRoutes from "./DashboardRoutes";
import ExploreRoutes from "./ExploreRoutes";
import FeedRoutes from "./FeedRoutes";
import SettingsRoutes from "./SettingsRoutes";
import JourneyRoutes from "./JourneyRoutes";
import ScoreRoutes from "./ScoreRoutes";
import AuditRoutes from "./AuditRoutes";
import CommonRoutes from "./CommonRoutes";

export default function ProtectedRoutes() {
  return (
    <Route path="/" element={<ProtectedRoute />}>
      <Route element={<AppLayout />}>
        {DashboardRoutes()}
        {ExploreRoutes()}
        {FeedRoutes()}
        {JourneyRoutes()}
        {ScoreRoutes()}
        {AuditRoutes()}
        {SettingsRoutes()}
        {CommonRoutes()}
      </Route>
    </Route>
  );
}
