import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";

import AppRoutes from "@/routes";

export default function App() {
  //! Reset password page shows error cause uuid and token error
  return (
    <BrowserRouter>
      <AppRoutes />
      
      <Toaster position="top-center" richColors closeButton />
    </BrowserRouter>
  );
}
