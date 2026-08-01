import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    q: "How do I create a journey?",
    a: 'Go to the Journeys page and click "New Journey." Fill in the details and click "Create".',
  },
  {
    q: "What is Builder Score?",
    a: "A reputation score that rewards consistent activity, engagement, and milestones. The higher your score, the more you've contributed to the community.",
  },
  {
    q: "Is JourneyHub free?",
    a: "Yes. Every feature is free right now. A Pro tier is in development. Nothing will charge you until it launches.",
  },
  {
    q: "Can I delete my account?",
    a: 'Yes. Visit Settings and choose "Delete Account". This action is permanent.',
  },
];

export default function Support() {
  return (
    <div className="flex h-full flex-col overflow-hidden px-6 py-6">
      <div className="mx-auto flex h-full w-full max-w-4xl flex-col">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold tracking-tight">Support Center</h1>

          <p className="mt-2 text-muted-foreground">
            Need help? Browse our FAQ or contact the JourneyHub team.
          </p>
        </div>

        <Separator className="mb-6" />

        <div className="grid gap-6">
          <Card className="rounded-2xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">Support Coming Soon</CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
              <p className="leading-7 text-muted-foreground">
                JourneyHub is currently under active development. Dedicated support channels,
                community discussions, and contact options will be available before the public
                launch.
              </p>

              <div className="rounded-xl border bg-muted/40 p-4">
                <h4 className="mb-3 font-medium">What's planned</h4>

                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>✓ In-app support center</li>
                  <li>✓ Community discussions</li>
                  <li>✓ Bug reporting system</li>
                  <li>✓ Feature request portal</li>
                  <li>✓ Dedicated support email</li>
                </ul>
              </div>

              <p className="text-sm text-muted-foreground">
                Until these features are available, support options are temporarily unavailable.
              </p>
            </CardContent>
          </Card>
        </div>

        <Card className="mt-6 flex-1 overflow-hidden rounded-2xl">
          <CardHeader>
            <CardTitle>Frequently Asked Questions</CardTitle>
          </CardHeader>

          <CardContent className="h-full overflow-y-auto">
            <Accordion type="single" collapsible className="w-full">
              {faqs.map((item, index) => (
                <AccordionItem key={item.q} value={`item-${index}`}>
                  <AccordionTrigger className="text-left font-medium hover:no-underline">
                    {item.q}
                  </AccordionTrigger>

                  <AccordionContent className="leading-6 text-muted-foreground">
                    {item.a}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </CardContent>
        </Card>

        <div className="mt-6 text-center">
          <p className="text-sm text-muted-foreground">
            JourneyHub is currently in active development. More plans and support options will be
            announced in future updates.
          </p>
        </div>
      </div>
    </div>
  );
}
