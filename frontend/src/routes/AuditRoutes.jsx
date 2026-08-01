import { Route } from "react-router-dom";
import ReportLogs from "@/pages/audit/ReportLogs";

export default function AuditRoutes() {
  return (
    <>
      <Route path="/logs" element={<ReportLogs />} />;
    </>
  );
}
