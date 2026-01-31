import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Smartphone,
  MessageCircle,
  Clock,
  Shield,
  Headphones,
  ArrowRight,
  CheckCircle,
} from "lucide-react";

const Index = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: MessageCircle,
      title: "24/7 Support",
      description:
        "Get help anytime, anywhere with round-the-clock customer support",
    },
    {
      icon: Clock,
      title: "Quick Resolution",
      description:
        "Fast response times and efficient problem solving for all your issues",
    },
    {
      icon: Shield,
      title: "Secure Platform",
      description:
        "Your data is protected with bank-level security and encryption",
    },
    {
      icon: Headphones,
      title: "Live Chat",
      description:
        "Real-time chat support with our expert customer service team",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-primary/10 to-background px-4 py-12">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <div className="w-20 h-20 bg-primary rounded-full flex items-center justify-center mx-auto mb-6">
            <Smartphone className="h-10 w-10 text-primary-foreground" />
          </div>

          <div className="space-y-4">
            <h1 className="text-4xl md:text-6xl font-bold text-foreground">
              Support Agent X
            </h1>
            <p className="text-xl md:text-2xl text-primary font-semibold">
              Customer Support Hub
            </p>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Your one-stop solution for all your support needs. Get instant
              help, track your requests, and resolve issues quickly.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-6">
            <Button
              size="lg"
              onClick={() => navigate("/login")}
              className="min-w-[200px]"
            >
              Get Support Now
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why Choose Us?</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Experience superior customer support with our comprehensive
              platform designed for seamless assistance
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="text-center hover:shadow-lg transition-shadow"
              >
                <CardHeader>
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription>{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-secondary text-secondary-foreground px-4 py-8">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Smartphone className="h-6 w-6" />
            <span className="text-xl font-bold">Support Agent X</span>
          </div>
          <p className="text-sm opacity-80">
            Your trusted partner for customer support
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center text-sm opacity-80">
            <span>Emergency: 1800-XXX-XXXX</span>
            <span>•</span>
            <span>Email: support@supportagentx.com</span>
          </div>
          <p className="text-xs opacity-60 pt-4">
            © {new Date().getFullYear()} Support Hub. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
