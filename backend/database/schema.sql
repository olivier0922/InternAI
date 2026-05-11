-- Users and Profiles
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    preferred_roles TEXT[] DEFAULT '{}',
    preferred_locations TEXT[] DEFAULT '{}',
    remote_only BOOLEAN DEFAULT FALSE,
    internship BOOLEAN DEFAULT FALSE,
    full_time BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Resumes
CREATE TABLE IF NOT EXISTS public.resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    parsed_text TEXT,
    extracted_skills JSONB DEFAULT '[]'::jsonb,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Jobs
CREATE TABLE IF NOT EXISTS public.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    remote BOOLEAN DEFAULT FALSE,
    description TEXT NOT NULL,
    salary TEXT,
    url TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    job_type TEXT DEFAULT 'Full-time',
    tags TEXT[] DEFAULT '{}',
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Matches
CREATE TABLE IF NOT EXISTS public.matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES public.jobs(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    matching_skills TEXT[] DEFAULT '{}',
    missing_skills TEXT[] DEFAULT '{}',
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    UNIQUE(user_id, job_id)
);

-- Applications Tracker
CREATE TABLE IF NOT EXISTS public.applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES public.jobs(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('Saved', 'Applied', 'Interview', 'Rejected', 'Offer')),
    notes TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    UNIQUE(user_id, job_id)
);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;

-- Profiles Policies
CREATE POLICY "Users can view their own profile." ON public.profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own profile." ON public.profiles FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own profile." ON public.profiles FOR UPDATE USING (auth.uid() = user_id);

-- Resumes Policies
CREATE POLICY "Users can view their own resumes." ON public.resumes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own resumes." ON public.resumes FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Jobs Policies (Jobs are public to view, only backend can insert)
CREATE POLICY "Jobs are viewable by everyone." ON public.jobs FOR SELECT USING (true);
-- Assuming service role for backend insertions bypassing RLS

-- Matches Policies
CREATE POLICY "Users can view their own matches." ON public.matches FOR SELECT USING (auth.uid() = user_id);

-- Applications Policies
CREATE POLICY "Users can view their own applications." ON public.applications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own applications." ON public.applications FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own applications." ON public.applications FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own applications." ON public.applications FOR DELETE USING (auth.uid() = user_id);
