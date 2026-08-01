import { Link } from "react-router-dom";
import { Check, Lock, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Everything JourneyHub offers today",
    features: [
      "Unlimited journeys",
      "Unlimited updates",
      "Likes, comments & replies",
      "Public profile & Builder Score",
      "Follow builders",
      "Community feed access",
    ],
    cta: "Get Started",
    available: true,
  },
  {
    name: "Pro",
    price: "$9",
    period: "per month",
    description: "Power features currently in development",
    features: [
      "Everything in Free",
      "Priority support",
      "Advanced analytics",
      "Custom branding",
      "Export your data",
    ],
    cta: "Coming Soon",
    available: false,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "contact us",
    description: "For teams and organizations",
    features: [
      "Everything in Pro",
      "Team collaboration",
      "SSO & enterprise security",
      "Dedicated support",
      "Custom integrations",
    ],
    cta: "Coming Soon",
    available: false,
  },
];

export default function Pricing() {
  return (
    <div className="mx-auto max-w-4xl  flex h-full flex-col">
      <div className="text-center">
        <Badge variant="secondary" className="mb-3 rounded-full px-4 py-1">
          <Sparkles className="mr-2 h-3.5 w-3.5" />
          Free During Early Access
        </Badge>

        <h1 className="text-4xl font-bold tracking-tight">
          Simple Pricing.
          <br />
          No Surprises.
        </h1>

        <p className="mx-auto mt-3 max-w-1xl text-muted-foreground">
          JourneyHub is completely free while we continue building the platform. Paid plans shown
          below are only our roadmap.
        </p>
      </div>

      <Separator className="my-5" />

      <div className="grid flex-1 gap-5 lg:grid-cols-3">
        {plans.map((plan) => (
          <Card
            key={plan.name}
            className={`flex h-full flex-col rounded-2xl transition-all duration-300 ${
              plan.available
                ? "border-primary shadow-lg shadow-primary/10 hover:-translate-y-1"
                : "hover:border-primary/40"
            }`}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle>{plan.name}</CardTitle>

                {plan.available ? (
                  <Badge>Live</Badge>
                ) : (
                  <Badge variant="secondary">
                    <Lock className="mr-1 h-3 w-3" />
                    Soon
                  </Badge>
                )}
              </div>

              <CardDescription className="mt-2">{plan.description}</CardDescription>

              <div className="mt-4 flex items-end gap-2">
                <span className="text-4xl font-bold">{plan.price}</span>

                <span className="pb-1 text-sm text-muted-foreground">/ {plan.period}</span>
              </div>
            </CardHeader>

            <CardContent className="flex-1 overflow-y-auto">
              <ul className="space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <div
                      className={`mt-0.5 flex h-5 w-5 items-center justify-center rounded-full ${
                        plan.available ? "bg-primary/10" : "bg-muted"
                      }`}
                    >
                      <Check
                        className={`h-3.5 w-3.5 ${
                          plan.available ? "text-primary" : "text-muted-foreground"
                        }`}
                      />
                    </div>

                    <span className={plan.available ? "text-sm" : "text-sm text-muted-foreground"}>
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>

            <CardFooter>
              {plan.available ? (
                <Button asChild className="w-full" size="lg">
                  <Link to="/dashboard">{plan.cta}</Link>
                </Button>
              ) : (
                <Button disabled variant="outline" className="w-full" size="lg">
                  <Lock className="mr-2 h-4 w-4" />
                  {plan.cta}
                </Button>
              )}
            </CardFooter>
          </Card>
        ))}
      </div>

      <div className="mt-6 text-center">
        <p className="text-sm text-muted-foreground">
          JourneyHub is currently in active development. More plans and support options will be
          announced in future updates.
        </p>
      </div>
    </div>
  );
}
