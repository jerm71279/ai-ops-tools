import { Card, CardContent } from "@/components/ui/card";
import { Star } from "lucide-react";

const testimonials = [
  {
    quote: "ComplianceOS transformed how we handle ISO 27001 compliance. The schema blocks and MCP Server made audit preparation seamless. We went from 8 weeks to 2 weeks.",
    author: "Devon Harris",
    role: "Owner",
    company: "OberaConnect - MSP Company",
    rating: 5,
  },
  {
    quote: "The modular architecture was exactly what we needed. Schema blocks like IR.1 and HR.8 integrate perfectly with our workflows. Compliance is now a competitive advantage.",
    author: "Evan Fisher",
    role: "CEO",
    company: "OberaConnect - MSP Company",
    rating: 5,
  },
  {
    quote: "Finally, a compliance platform that understands business needs. The clause-aware backbone and workflow automation have been game-changing for our operations.",
    author: "Michael Rodriguez",
    role: "VP of Operations",
    company: "HealthFlow Systems",
    rating: 5,
  },
  {
    quote: "The workflow integration saved us months of custom development. We consolidated four frameworks into one platform with unified reporting.",
    author: "Emily Thompson",
    role: "Head of Compliance",
    company: "FinServe Global",
    rating: 5,
  },
  {
    quote: "Audit preparation went from a nightmare to a smooth process. The automated evidence collection and MCP Server's clause resolution are brilliant.",
    author: "David Park",
    role: "Director of Risk",
    company: "CloudScale Solutions",
    rating: 5,
  },
  {
    quote: "We consolidated three different tools into ComplianceOS. The ROI was clear within the first quarter, and our team loves the unified interface.",
    author: "Lisa Martinez",
    role: "Chief Compliance Officer",
    company: "Enterprise Dynamics",
    rating: 5,
  },
];

const stats = [
  { value: "100+", label: "Enterprise Customers" },
  { value: "99.9%", label: "Audit Success Rate" },
  { value: "50%", label: "Time Savings" },
  { value: "4.9/5", label: "Customer Rating" },
];

const Testimonials = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Trusted by Leading Organizations
          </h2>
          <p className="text-xl text-muted-foreground">
            See what compliance leaders are saying about transforming their operations with ComplianceOS.
          </p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16 max-w-4xl mx-auto">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-accent mb-2">
                {stat.value}
              </div>
              <div className="text-sm text-muted-foreground">
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <Card 
              key={index} 
              className="border-border hover:shadow-elevated transition-all duration-300"
            >
              <CardContent className="pt-6">
                {/* Rating */}
                <div className="flex gap-1 mb-4">
                  {Array.from({ length: testimonial.rating }).map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-warning text-warning" />
                  ))}
                </div>

                {/* Quote */}
                <p className="text-foreground mb-6 leading-relaxed">
                  "{testimonial.quote}"
                </p>

                {/* Author */}
                <div className="border-t border-border pt-4">
                  <div className="font-semibold text-foreground">
                    {testimonial.author}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {testimonial.role}
                  </div>
                  <div className="text-sm text-accent font-medium mt-1">
                    {testimonial.company}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Trust Badge */}
        <div className="mt-16 text-center">
          <p className="text-sm text-muted-foreground mb-4">
            Trusted by leading MSP companies and organizations including OberaConnect
          </p>
          <div className="flex flex-wrap items-center justify-center gap-6">
            {["ISO 27001 Certified", "SOC 2 Type II", "GDPR Compliant", "HIPAA Ready"].map((badge, idx) => (
              <div
                key={idx}
                className="px-4 py-2 bg-accent/10 border border-accent/20 rounded-full text-sm font-medium text-accent"
              >
                {badge}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
