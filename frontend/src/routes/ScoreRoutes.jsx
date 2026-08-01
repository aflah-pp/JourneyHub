import { Route } from "react-router-dom";
import MyScore from "@/pages/score/MyScore";
import Leaderboard from "@/pages/score/Leaderboard";
import ReportLogs from "@/pages/audit/ReportLogs";

export default function ScoreRoutes() {
  return (
    <>
      <Route path="/score/self" element={<MyScore />} />
      <Route path="/score/leaderboard" element={<Leaderboard />} />
      <Route path="/logs" element={<ReportLogs />} />;
    </>
  );
}
