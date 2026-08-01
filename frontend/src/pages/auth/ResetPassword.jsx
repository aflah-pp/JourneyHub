import { AuthLayout } from "@/components/layout/authLayout";
import { ResetPasswordForm } from "@/components/auth/reset-password-form";

function ResetPassword() {
  return (
    <AuthLayout>
      <ResetPasswordForm />
    </AuthLayout>
  );
}

export default ResetPassword;
