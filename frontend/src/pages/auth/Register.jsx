import { AuthLayout } from "@/components/layout/authLayout";
import { RegisterForm } from "@/components/auth/register-form";

function Register() {
  return (
    <AuthLayout>
      <RegisterForm />
    </AuthLayout>
  );
}

export default Register;
