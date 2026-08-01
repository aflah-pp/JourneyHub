import { Routes } from "react-router-dom";

import AuthRoutes from "./AuthRoutes";
import ProtectedRoutes from "./ProtectedRoutes";

export default function AppRoutes() {
  return (
    <Routes>
      {AuthRoutes()}
      {ProtectedRoutes()}
    </Routes>
  );
}
