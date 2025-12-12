import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

const plans = [
  {
    name: "Starter",
    price: "$499",
    period: "per month",
    description: "Perfect for small teams getting started with compliance",
    features: [
      "Up to 100 controls",
      "2 framework mappings",
      "Basic workflow integration",
      "Email support",
      "Audit trail logging",
      "Standard reporting",
      "5 team members",
    ],
    cta: "Start Free Trial",
    popular: false,
  },
  {
    name: "Professional",
    price: "$1,499",
    period: "per month",
    description: "For growing organizations with complex compliance needs",
    features: [
      "Unlimited controls",
      "All framework mappings",
      "Advanced workflow automation",
      "Priority support + CSM",
      "Custom schema builder",
      "Advanced analytics",
      "Unlimited team members",
      "API access",
      "Custom integrations",
    ],
    cta: "Start Free Trial",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "contact us",
    description: "Tailored solutions for large enterprises",
    features: [
      "Everything in Professional",
      "Dedicated infrastructure",
      "Custom framework support",
      "White-label options",
      "24/7 phone support",
      "Onboarding + training",
      "SLA guarantees",
      "Custom development",
      "Legal review support",
    ],
    cta: "Contact Sales",
    popular: false,
  },
];

const Pricing = () => {
  const navigate = useNavigate();

  const handleCTAClick = (planName: string) => {
    if (planName === "Enterprise") {
      // Scroll to contact section or open email
      window.location.href = "mailto:sales@oberaconnect.com?subject=Enterprise Plan Inquiry";
    } else {
      navigate('/auth');
    }
  };
  return (
    <section className="py-24 bg-secondary/30" id="pricing">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-muted-foreground">
            Choose the plan that fits your organization's needs. All plans include 14-day free trial.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {plans.map((plan, index) => (
            <Card 
              key={index} 
              className={`border-border relative ${
                plan.popular 
                  ? "shadow-floating border-accent/50 scale-105" 
                  : "hover:shadow-elevated"
              } transition-all duration-300`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <Badge className="bg-gradient-accent text-white border-0 px-4 py-1">
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl mb-2">{plan.name}</CardTitle>
                <div className="mb-2">
                  <span className="text-5xl font-bold">{plan.price}</span>
                  {plan.price !== "Custom" && (
                    <span className="text-muted-foreground ml-2">/{plan.period}</span>
                  )}
                  {plan.price === "Custom" && (
                    <span className="text-muted-foreground ml-2 text-lg">{plan.period}</span>
                  )}
                </div>
                <CardDescription className="text-base">
                  {plan.description}
                </CardDescription>
              </CardHeader>

              <CardContent>
                {/* Features List */}
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Check className="h-3 w-3 text-accent" />
                      </div>
                      <span className="text-sm text-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>

                {/* CTA Button */}
                <Button
                  variant={plan.popular ? "hero" : "outline"}
                  size="lg"
                  className="w-full"
                  onClick={() => handleCTAClick(plan.name)}
                >
                  {plan.cta}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Additional Info */}
        <div className="mt-16 text-center max-w-2xl mx-auto">
          <p className="text-muted-foreground mb-4">
            All plans include free SSL, daily backups, and 99.9% uptime guarantee.
          </p>
          <p className="text-sm text-muted-foreground">
            Need a custom plan? <a href="#contact" className="text-accent hover:underline font-medium">Contact our sales team</a> for volume discounts and custom frameworks.
          </p>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
