import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

export default function Terms() {
  return (
    <div className="h-full overflow-y-auto px-6 py-6">
      <div className="mx-auto max-w-4xl">
        <Card className="border-border/60 shadow-sm">
          <CardHeader>
            <CardTitle className="text-2xl font-bold tracking-tight">Terms of Service</CardTitle>
            <p className="text-sm text-muted-foreground">Last updated: August 1, 2026</p>
          </CardHeader>
          <CardContent className="space-y-7 text-sm leading-relaxed">
            <section className="space-y-2">
              <h2 className="text-lg font-semibold">1. Acceptance of terms</h2>
              <p className="text-muted-foreground">
                By using JourneyHub ("the Service"), you agree to these Terms of Service. If you
                don't agree, please don't use the Service.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold">2. Description of Service</h2>
              <p className="text-muted-foreground">
                JourneyHub is a social platform for documenting the process of building things.
                Users create journeys, post updates, interact with other builders, and earn a
                Builder Score.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold">3. User accounts</h2>
              <ul className="list-disc pl-6 space-y-1.5 text-muted-foreground">
                <li>You must be at least 13 years old to use the Service.</li>
                <li>
                  You must verify your email before posting content — browsing is open without
                  verification.
                </li>
                <li>You're responsible for keeping your account credentials confidential.</li>
                <li>You agree to provide accurate information during registration.</li>
                <li>You may not impersonate another person or entity.</li>
              </ul>
            </section>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold">4. User content</h2>
              <p className="text-muted-foreground">
                You retain ownership of all content you post. By posting, you grant JourneyHub a
                worldwide, non-exclusive, royalty-free license to display, distribute, and promote
                your content within the Service.
              </p>
              <p className="text-muted-foreground">
                You agree not to post content that is illegal, harmful, threatening, abusive,
                harassing, defamatory, vulgar, obscene, or otherwise objectionable.
              </p>
            </section>

            <section className="space-y-2">
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-semibold">5. Pro subscription</h2>
                <Badge variant="secondary" className="text-xs">
                  Not yet available
                </Badge>
              </div>
              <p className="text-muted-foreground">
                JourneyHub is currently free in full. The Pro and Enterprise tiers described on our
                Pricing page are planned features, not active billing plans — nothing on this
                Service will charge you until a paid tier actually launches. When it does, this
                section will be updated with renewal terms and our refund policy before any charges
                begin.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold">6. Termination</h2>
              <p className="text-muted-foreground">
                We may suspend or terminate your account if you violate these Terms. You can delete
                your account at any time from Settings.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold">7. Limitation of liability</h2>
              <p className="text-muted-foreground">
                JourneyHub is provided "as is" without warranties of any kind. We're not liable for
                damages arising from your use of the Service.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold">8. Changes to Terms</h2>
              <p className="text-muted-foreground">
                We may update these Terms as the Service evolves. We'll notify you of significant
                changes by email or a notice on the Service.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold">9. Contact</h2>
              <p className="text-sm text-muted-foreground">
                JourneyHub is currently in active development. More plans and support options will
                be announced in future updates.
              </p>
            </section>
            <div className="mt-6 text-center"></div>

            <Separator />

            <p className="text-xs text-muted-foreground">
              By continuing to use the Service, you agree to these Terms.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
