'use client'

import { JobDetailPane } from '@/app/dashboard/JobDetailPane'

const mockJob = {
  id: '123',
  title: 'Senior Software Engineer, Frontend',
  company: 'Stripe',
  description: 'We are looking for a Senior Software Engineer to join our frontend team.\n\nRequirements:\n- 5+ years of React experience\n- Strong CSS skills\n- Experience with Next.js\n\nBenefits:\n- Competitive salary\n- Remote work\n- Health insurance',
  location: 'San Francisco, CA',
  remote: true,
  salary: '$150k - $200k',
  job_type: 'Full-time',
  source: 'Direct',
  created_at: new Date().toISOString(),
  tags: ['React', 'TypeScript', 'Next.js'],
  url: 'https://stripe.com/jobs',
  relevanceScore: 95
}

export default function TestPage() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-8">
      <div className="w-[450px] h-[calc(100vh-100px)]">
        <JobDetailPane job={mockJob} isSaved={false} />
      </div>
    </div>
  )
}
