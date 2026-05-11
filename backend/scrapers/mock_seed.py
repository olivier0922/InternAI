import os
from dotenv import load_dotenv

load_dotenv()
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from supabase import create_client, Client
from schemas.job import JobCreate

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(url, key)

jobs = [
    JobCreate(title="Software Engineering Intern", company="OpenAI", location="San Francisco, CA", remote=False, description="Join our team to build the next generation of AI models. Strong Python and C++ skills required.", url="https://openai.com/careers/1", source="Direct"),
    JobCreate(title="Full Stack Engineer - New Grad", company="Vercel", location="Remote", remote=True, description="Help us build the best platform for frontend developers. Experience with React and Next.js is a plus.", url="https://vercel.com/careers/2", source="Direct"),
    JobCreate(title="Backend Intern", company="Anthropic", location="Remote", remote=True, description="Work on scalable infrastructure for our language models. Rust and Go experience preferred.", url="https://anthropic.com/careers/3", source="Direct"),
    JobCreate(title="Frontend Developer Intern", company="Shopify", location="Montreal, QC", remote=False, description="Build beautiful commerce experiences. Strong React and CSS skills required.", url="https://shopify.com/careers/4", source="Direct"),
    JobCreate(title="Machine Learning Intern", company="Mila", location="Montreal, QC", remote=False, description="Research applied machine learning for reinforcement learning applications. PyTorch experience required.", url="https://mila.quebec/careers/5", source="Direct"),
    JobCreate(title="Data Engineer", company="SSENSE", location="Montreal, QC", remote=True, description="Manage data pipelines for global e-commerce. Python, Airflow, and Snowflake experience required.", url="https://ssense.com/careers/6", source="Direct"),
    JobCreate(title="Cloud Infrastructure Intern", company="AWS", location="Toronto, ON", remote=False, description="Scale massive cloud systems. Experience with Linux, networking, and Python/Go.", url="https://aws.amazon.com/careers/7", source="Direct"),
    JobCreate(title="Mobile App Developer Intern", company="Transit", location="Montreal, QC", remote=False, description="Help millions of people navigate their cities. Swift and Kotlin experience preferred.", url="https://transitapp.com/careers/8", source="Direct"),
    JobCreate(title="Software Developer Intern", company="Ubisoft", location="Montreal, QC", remote=False, description="Core engine development for AAA titles. C++ profiling and optimization.", url="https://ubisoft.com/careers/9", source="Direct"),
    JobCreate(title="Security Engineer Intern", company="1Password", location="Toronto, ON", remote=True, description="Keep user data secure. Rust and cryptography knowledge required.", url="https://1password.com/careers/10", source="Direct"),
    JobCreate(title="AI Research Scientist", company="Google DeepMind", location="Montreal, QC", remote=False, description="Fundamental AI research. PhD preferred, strong theoretical background.", url="https://deepmind.com/careers/11", source="Direct"),
    JobCreate(title="Full Stack Intern", company="Wealthsimple", location="Toronto, ON", remote=True, description="Build financial tools. Ruby on Rails and React.", url="https://wealthsimple.com/careers/12", source="Direct"),
    JobCreate(title="Backend Developer (Go)", company="Discord", location="Remote", remote=True, description="Scale real-time communications. Go and Elixir.", url="https://discord.com/careers/13", source="Direct"),
    JobCreate(title="Frontend Engineer", company="Figma", location="San Francisco, CA", remote=False, description="Build complex web-based design tools. TypeScript, WebGL, C++ (WebAssembly).", url="https://figma.com/careers/14", source="Direct"),
    JobCreate(title="Game Developer Intern", company="Behaviour Interactive", location="Montreal, QC", remote=False, description="Unreal Engine gameplay programming. C++ and Blueprints.", url="https://bhvr.com/careers/15", source="Direct"),
    JobCreate(title="SRE Intern", company="Cloudflare", location="Remote", remote=True, description="Keep the internet fast and secure. Linux internals, Go, Rust.", url="https://cloudflare.com/careers/16", source="Direct"),
    JobCreate(title="Software Engineer, Product", company="Stripe", location="Seattle, WA", remote=True, description="Build economic infrastructure. Ruby, React, Flow.", url="https://stripe.com/careers/17", source="Direct"),
    JobCreate(title="Data Scientist Intern", company="Spotify", location="New York, NY", remote=False, description="Analyze user listening habits. Python, SQL, BigQuery.", url="https://spotify.com/careers/18", source="Direct"),
    JobCreate(title="Full Stack Software Engineer", company="GitHub", location="Remote", remote=True, description="Build tools for developers. Ruby on Rails, React, Go.", url="https://github.com/careers/19", source="Direct"),
    JobCreate(title="Systems Software Engineer", company="NVIDIA", location="Santa Clara, CA", remote=False, description="Optimize CUDA libraries. C, C++, Parallel Programming.", url="https://nvidia.com/careers/20", source="Direct"),
    JobCreate(title="Developer Advocate", company="Supabase", location="Remote", remote=True, description="Help developers build with Supabase. Next.js, Postgres, TypeScript.", url="https://supabase.com/careers/21", source="Direct"),
    JobCreate(title="Software Engineer Intern", company="Hopper", location="Montreal, QC", remote=True, description="Travel tech backend systems. Scala, GCP, microservices.", url="https://hopper.com/careers/22", source="Direct"),
    JobCreate(title="Computer Vision Intern", company="Tesla", location="Palo Alto, CA", remote=False, description="Autopilot perception stack. PyTorch, C++, TensorRT.", url="https://tesla.com/careers/23", source="Direct"),
    JobCreate(title="React Native Developer", company="Brex", location="Remote", remote=True, description="Build modern financial software. React Native, TypeScript.", url="https://brex.com/careers/24", source="Direct"),
    JobCreate(title="Robotics Engineer", company="Boston Dynamics", location="Waltham, MA", remote=False, description="Control systems for advanced robots. C++, Python, ROS.", url="https://bostondynamics.com/careers/25", source="Direct"),
]

for job in jobs:
    existing = supabase.table("jobs").select("id").eq("url", job.url).execute()
    if not existing.data:
        supabase.table("jobs").insert(job.model_dump()).execute()
        print(f"Inserted: {job.title} at {job.company}")
