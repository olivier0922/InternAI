import Link from "next/link";
import {
  Brain,
  Kanban,
  Sparkles,
  ArrowRight,
  Zap,
  Globe,
  Shield,
  Search,
  BarChart3,
} from "lucide-react";

export default function Home() {
  return (
    <div className="relative flex flex-col min-h-[calc(100dvh-64px)] overflow-hidden">
      <div className="mesh-bg" />

      {/* Hero */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pb-safe pt-12 md:pt-20">
        <div className="space-y-6 max-w-3xl">

          {/* Heading */}
          <h1 className="text-4xl sm:text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.1]">
            <span className="block">Your next</span>
            <span className="gradient-text inline-block">engineering role</span>
            <span className="block">starts here.</span>
          </h1>

          {/* Subheading */}
          <p className="mx-auto max-w-xl text-[15px] sm:text-base md:text-lg text-muted-foreground leading-relaxed px-4">
            Real-time job aggregation. AI resume matching. Application tracking. One platform built specifically for engineering students.
          </p>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2 px-4 sm:px-0">
            <Link href="/signup" className="w-full sm:w-auto">
              <button className="w-full sm:w-auto gradient-btn text-white font-semibold px-7 py-3.5 sm:py-3 rounded-xl text-sm flex items-center justify-center gap-2">
                Start Free <ArrowRight className="w-4 h-4" />
              </button>
            </Link>
            <Link href="/login" className="w-full sm:w-auto">
              <button className="w-full sm:w-auto glass text-foreground font-medium px-7 py-3.5 sm:py-3 rounded-xl text-sm hover:bg-white/[0.06] transition-colors">
                Sign In
              </button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-16 sm:mt-24 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl w-full">
          {[
            {
              icon: Search,
              title: "Real-time search",
              desc: "Instant results as you type. Search across hundreds of jobs from LinkedIn, Indeed, Glassdoor, Remotive, Arbeitnow, and Hacker News.",
            },
            {
              icon: Brain,
              title: "AI resume matching",
              desc: "Upload your resume. Our LLM analyzes every job listing and gives you a compatibility score.",
            },
            {
              icon: Kanban,
              title: "Application tracker",
              desc: "Kanban board to move jobs from Saved → Applied → Interview → Offer.",
            },
            {
              icon: Globe,
              title: "Remote-first",
              desc: "One-click filter for remote roles. Location tags from real job data.",
            },
            {
              icon: BarChart3,
              title: "Skill gap analysis",
              desc: "See which skills you have and which you're missing for each role.",
            },
            {
              icon: Shield,
              title: "Secure & private",
              desc: "Your resume and data stay encrypted. We never share with third parties.",
            },
          ].map((f) => (
            <div key={f.title} className="glass-card rounded-xl p-5 sm:p-6 text-left">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <f.icon className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-semibold text-[15px] mb-2">{f.title}</h3>
              <p className="text-[13px] text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 py-6 text-center text-xs text-muted-foreground/60 border-t border-white/[0.04]">
        © {new Date().getFullYear()} InternAI · Built for engineering students
      </footer>
    </div>
  );
}
