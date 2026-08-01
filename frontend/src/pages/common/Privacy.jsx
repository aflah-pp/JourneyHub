import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export default function Privacy() {
  return (
    <div className="flex h-full justify-center">
      <Card className="flex h-full w-full max-w-4xl flex-col overflow-hidden rounded-2xl shadow-sm">
        <CardHeader className="border-b">
          <CardTitle className="text-2xl font-bold tracking-tight">Privacy Policy</CardTitle>

          <p className="text-sm text-muted-foreground">Last updated: August 1, 2026</p>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-8">
          <div className="space-y-8 text-sm leading-7">
            <section className="space-y-3">
              <h2 className="text-lg font-semibold">1. Information we collect</h2>

              <ul className="list-disc space-y-2 pl-6 text-muted-foreground">
                <li>
                  <strong className="text-foreground">Account data:</strong> username, email address
                  and password (stored only as a secure salted hash).
                </li>

                <li>
                  <strong className="text-foreground">Profile data:</strong> bio, avatar, location,
                  website and any optional links you choose to provide.
                </li>

                <li>
                  <strong className="text-foreground">Content:</strong> journeys, updates, comments,
                  replies and saved items.
                </li>

                <li>
                  <strong className="text-foreground">Usage data:</strong> pages visited, searches
                  and feature usage.
                </li>

                <li>
                  <strong className="text-foreground">Device data:</strong> IP address, browser and
                  operating system.
                </li>
              </ul>
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="text-lg font-semibold">2. How we use your information</h2>

              <ul className="list-disc space-y-2 pl-6 text-muted-foreground">
                <li>Provide and improve JourneyHub.</li>
                <li>Calculate your Builder Score.</li>
                <li>Deliver personalized content.</li>
                <li>Send account notifications and emails.</li>
                <li>Prevent abuse, spam and fraud.</li>
                <li>Enforce our Terms of Service.</li>
              </ul>
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="text-lg font-semibold">3. Sharing your information</h2>

              <p className="text-muted-foreground">
                We never sell your personal information. Data is only shared when necessary with
                trusted providers.
              </p>

              <ul className="list-disc space-y-2 pl-6 text-muted-foreground">
                <li>Cloudinary for media storage.</li>
                <li>Email provider for account emails.</li>
                <li>Authorities where legally required.</li>
                <li>Public profile information visible to other users.</li>
              </ul>
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="text-lg font-semibold">4. Authentication & Security</h2>

              <p className="text-muted-foreground">
                JourneyHub authenticates users using JWT access and refresh tokens. Tokens are
                rotated and revoked on logout. Passwords are securely hashed and never stored in
                plain text.
              </p>
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="text-lg font-semibold">5. Data security</h2>

              <p className="text-muted-foreground">
                We sanitize submitted content and use industry-standard security practices to
                protect user information. While we take security seriously, no online service can
                guarantee absolute protection.
              </p>
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="text-lg font-semibold">6. Your rights</h2>

              <ul className="list-disc space-y-2 pl-6 text-muted-foreground">
                <li>Access your personal data.</li>
                <li>Update or delete your profile.</li>
                <li>Export your JourneyHub data.</li>
                <li>Request a copy of stored information.</li>
              </ul>
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="text-lg font-semibold">7. Cookies</h2>

              <p className="text-muted-foreground">
                Authentication does not rely on cookies. Limited cookies may be used for preferences
                such as theme selection.
              </p>
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="text-lg font-semibold">8. Third-party links</h2>

              <p className="text-muted-foreground">
                External websites linked from JourneyHub have their own privacy policies and
                practices.
              </p>
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="text-lg font-semibold">9. Children's privacy</h2>

              <p className="text-muted-foreground">
                JourneyHub is intended for users aged 13 years or older. We do not knowingly collect
                information from children under 13.
              </p>
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="text-lg font-semibold">10. Changes to this policy</h2>

              <p className="text-muted-foreground">
                This Privacy Policy may change as JourneyHub evolves. Major updates will be
                communicated through the platform or by email.
              </p>
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="text-lg font-semibold">11. Contact</h2>
              <p className="text-sm text-muted-foreground">
                JourneyHub is currently in active development. More plans and support options will
                be announced in future updates.
              </p>
            </section>

            <Separator />

            <p className="text-center text-xs text-muted-foreground">
              By using JourneyHub, you acknowledge and agree to this Privacy Policy.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
