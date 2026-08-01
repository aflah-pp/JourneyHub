import { AuthLayout } from "@/components/layout/authLayout";
import { LoginForm } from "@/components/auth/login-form";

function Login() {
  return (
    <AuthLayout>
      <LoginForm />
    </AuthLayout>
  );
}

export default Login;
