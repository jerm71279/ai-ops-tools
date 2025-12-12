import { Shield } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import oberaLogo from "@/assets/obera-logo.png";

const Footer = () => {
  const currentYear = new Date().getFullYear();
  const navigate = useNavigate();

  const scrollToSection = (sectionId: string) => {
    if (window.location.pathname !== '/') {
      navigate('/');
      setTimeout(() => {
        const element = document.getElementById(sectionId);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    } else {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  };

  return (
    <footer className="bg-primary text-primary-foreground py-12 border-t border-border">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center mb-4 hover:opacity-80 transition-opacity">
              <img 
                src={oberaLogo} 
                alt="OberaConnect Logo" 
                className="h-12 w-auto brightness-0 invert"
              />
            </Link>
            <p className="text-sm text-primary-foreground/70">
              Enterprise operational intelligence platform for modern businesses.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-sm text-primary-foreground/70">
              <li>
                <button onClick={() => scrollToSection('features')} className="hover:text-primary-foreground transition-colors">
                  Features
                </button>
              </li>
              <li>
                <button onClick={() => scrollToSection('frameworks')} className="hover:text-primary-foreground transition-colors">
                  Frameworks
                </button>
              </li>
              <li>
                <button onClick={() => scrollToSection('pricing')} className="hover:text-primary-foreground transition-colors">
                  Pricing
                </button>
              </li>
              <li>
                <Link to="/integrations" className="hover:text-primary-foreground transition-colors">
                  Integrations
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-primary-foreground/70">
              <li>
                <Link to="/developers" className="hover:text-primary-foreground transition-colors">
                  Developer Portal
                </Link>
              </li>
              <li><a href="#docs" className="hover:text-primary-foreground transition-colors">Documentation</a></li>
              <li><a href="#blog" className="hover:text-primary-foreground transition-colors">Blog</a></li>
              <li><a href="#guides" className="hover:text-primary-foreground transition-colors">Compliance Guides</a></li>
              <li><a href="#api" className="hover:text-primary-foreground transition-colors">API Reference</a></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-primary-foreground/70">
              <li><a href="#about" className="hover:text-primary-foreground transition-colors">About Us</a></li>
              <li><a href="#contact" className="hover:text-primary-foreground transition-colors">Contact</a></li>
              <li><a href="#careers" className="hover:text-primary-foreground transition-colors">Careers</a></li>
              <li><a href="#security" className="hover:text-primary-foreground transition-colors">Security</a></li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-primary-foreground/10">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-primary-foreground/70">
            <p>© {currentYear} OberaConnect. All rights reserved.</p>
            <div className="flex gap-6">
              <a href="#privacy" className="hover:text-primary-foreground transition-colors">Privacy Policy</a>
              <a href="#terms" className="hover:text-primary-foreground transition-colors">Terms of Service</a>
              <a href="#cookies" className="hover:text-primary-foreground transition-colors">Cookie Policy</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
