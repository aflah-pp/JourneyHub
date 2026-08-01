import { Route } from "react-router-dom";
import Pricing from "@/pages/common/Pricing";
import Terms from "@/pages/common/Terms";
import Privacy from "@/pages/common/Privacy";
import Feedback from "@/pages/common/FeedBack";
import Support from "@/pages/common/Support";

export default function CommonRoutes() {
  return (
    <>
      <Route path="/pricing" element={<Pricing />} />
      <Route path="/terms" element={<Terms />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/support" element={<Support />} />
      <Route path="/feedback" element={<Feedback />} />
    </>
  );
}
