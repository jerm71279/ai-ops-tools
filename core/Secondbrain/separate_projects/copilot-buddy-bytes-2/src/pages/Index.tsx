import Navigation from "@/components/Navigation";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import MLIntelligence from "@/components/MLIntelligence";
import Frameworks from "@/components/Frameworks";
import DashboardPreview from "@/components/DashboardPreview";
import CaseStudy from "@/components/CaseStudy";
import UseCases from "@/components/UseCases";
import Integrations from "@/components/Integrations";
import Testimonials from "@/components/Testimonials";
import Pricing from "@/components/Pricing";
import CallToAction from "@/components/CallToAction";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen scroll-smooth">
      <Navigation />
      <main>
        <Hero />
        <div id="features">
          <Features />
        </div>
        <MLIntelligence />
        <div id="frameworks">
          <Frameworks />
        </div>
        <div id="dashboard">
          <DashboardPreview />
        </div>
        <div id="case-study">
          <CaseStudy />
        </div>
        <UseCases />
        <Integrations />
        <Testimonials />
        <div id="pricing">
          <Pricing />
        </div>
        <CallToAction />
      </main>
      <Footer />
    </div>
  );
};

export default Index;
