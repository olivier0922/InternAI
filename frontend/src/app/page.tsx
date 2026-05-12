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
    <div className="relative flex flex-col min-h-screen overflow-hidden">
      <div className="mesh-bg" />

      {/* Navigation */}
      <header className="relative z-10 px-6 py-5 flex items-center justify-between max-w-6xl mx-auto w-full">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg gradient-btn flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight">InternAI</span>
        </Link>
        <nav className="flex items-center gap-4">
          <Link
            href="/login"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Log in
          </Link>
          <Link href="/signup">
            <button className="gradient-btn text-white text-sm font-medium px-4 py-2 rounded-lg">
              Get Started
            </button>
          </Link>
        </nav>
      </header>

      {/* Hero */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pb-20">
        <div className="space-y-6 max-w-3xl">

          {/* Heading */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight leading-[1.08]">
            <span className="block">Your next</span>
            <span className="gradient-text inline-block">engineering role</span>
            <span className="block">starts here.</span>
          </h1>

          {/* Subheading */}
          <p className="mx-auto max-w-xl text-base md:text-lg text-muted-foreground leading-relaxed">
            Real-time job aggregation. AI resume matching. Application tracking. One platform built specifically for engineering students.
          </p>

          {/* CTA */}
          <div className="flex gap-3 justify-center pt-2">
            <Link href="/signup">
              <button className="gradient-btn text-white font-semibold px-7 py-3 rounded-xl text-sm flex items-center gap-2">
                Start Free <ArrowRight className="w-4 h-4" />
              </button>
            </Link>
            <Link href="/login">
              <button className="glass text-foreground font-medium px-7 py-3 rounded-xl text-sm hover:bg-white/[0.06] transition-colors">
                Sign In
              </button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-24 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl w-full">
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
            <div key={f.title} className="glass-card rounded-xl p-5 text-left">
              <f.icon className="w-5 h-5 text-primary mb-3" />
              <h3 className="font-semibold text-sm mb-1.5">{f.title}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{f.desc}</p>
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
