'use client'

import { MapPin, Globe, Building2, ExternalLink, Tag, Clock } from 'lucide-react'
import { JobCardActions } from './JobCardActions'
import type { ScoredJob } from './useJobFilters'
import { companyColor } from './HorizontalJobCard'

function timeAgo(dateStr: string): string {
  const now = Date.now()
  const then = new Date(dateStr).getTime()
  const diffMs = now - then
  const mins = Math.floor(diffMs / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  if (days < 30) return `${Math.floor(days / 7)}w ago`
  return `${Math.floor(days / 30)}mo ago`
}

export function JobDetailPane({ job, isSaved }: { job: ScoredJob; isSaved: boolean }) {
  const initials = job.company.split(/\s+/).map(w => w[0]).join('').substring(0, 2).toUpperCase()

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#09090b] sm:rounded-2xl border border-white/[0.08] shadow-2xl relative">
      {/* Header */}
      <div className="shrink-0 p-5 sm:p-8 border-b border-white/[0.06] relative overflow-hidden">
        {/* Subtle Background Glow */}
        <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-primary/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 pointer-events-none" />

        <div className="relative flex items-start justify-between mb-5 sm:mb-6">
          <div className="flex items-center gap-3 sm:gap-4 pr-8">
            <div className={`w-12 h-12 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br ${companyColor(job.company)} flex items-center justify-center text-white text-lg sm:text-xl font-bold shadow-[0_0_20px_rgba(99,102,241,0.3)] border border-white/10 shrink-0`}>
              {initials}
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold leading-tight tracking-tight mb-1">{job.title}</h2>
              <div className="flex flex-wrap items-center gap-2 sm:gap-2.5 text-[13px] sm:text-[14px] text-muted-foreground font-medium">
                <div className="flex items-center gap-1.5">
                  <Building2 className="w-3.5 h-3.5 text-primary/70" />
                  <span className="text-foreground/90">{job.company}</span>
                </div>
                <span className="w-1 h-1 rounded-full bg-white/20 hidden sm:block" />
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{timeAgo(job.created_at)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Info Chips */}
        <div className="flex flex-wrap gap-2 relative">
          {job.location && (
            <span className="inline-flex items-center gap-1.5 text-[12px] font-semibold px-2.5 py-1.5 sm:px-3 rounded-lg bg-white/[0.04] text-muted-foreground border border-white/[0.08]">
              <MapPin className="w-3.5 h-3.5 text-muted-foreground/70" />{job.location}
            </span>
          )}
          {job.remote && (
            <span className="inline-flex items-center gap-1.5 text-[12px] font-bold px-2.5 py-1.5 sm:px-3 rounded-lg bg-indigo-500/[0.08] text-indigo-300 border border-indigo-500/[0.15]">
              <Globe className="w-3.5 h-3.5" />Remote
            </span>
          )}
          {job.salary && (
            <span className="inline-flex items-center gap-1.5 text-[12px] font-bold px-2.5 py-1.5 sm:px-3 rounded-lg bg-emerald-500/[0.08] text-emerald-300 border border-emerald-500/[0.15]">
              💰 {job.salary}
            </span>
          )}
          {job.job_type && (
            <span className="inline-flex items-center gap-1.5 text-[12px] font-bold px-2.5 py-1.5 sm:px-3 rounded-lg bg-amber-500/[0.08] text-amber-300 border border-amber-500/[0.15]">
              {job.job_type}
            </span>
          )}
          <span className="inline-flex items-center gap-1.5 text-[12px] font-semibold px-2.5 py-1.5 sm:px-3 rounded-lg bg-white/[0.04] text-muted-foreground border border-white/[0.08]">
            Source: {job.source}
          </span>
        </div>
      </div>

      {/* Scrollable Body */}
      <div className="flex-1 min-h-0 overflow-y-auto p-5 sm:p-8 space-y-6 sm:space-y-8 custom-scrollbar pb-24 sm:pb-8">
        {/* Tags */}
        {job.tags && job.tags.length > 0 && (
          <div>
            <h4 className="text-[11px] font-bold text-muted-foreground/60 uppercase tracking-widest mb-3 flex items-center gap-2">
              <Tag className="w-3.5 h-3.5" /> Skills & Tags
            </h4>
            <div className="flex flex-wrap gap-2">
              {job.tags.map(tag => (
                <span key={tag} className="text-[12px] font-medium px-3 py-1.5 rounded-lg bg-white/[0.03] text-muted-foreground border border-white/[0.08] hover:bg-white/[0.06] transition-colors">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Description */}
        <div>
          <h4 className="text-[11px] font-bold text-muted-foreground/60 uppercase tracking-widest mb-3 sm:mb-4 flex items-center gap-2">
            <ExternalLink className="w-3.5 h-3.5" /> Job Description
          </h4>
          <div className="text-[14px] sm:text-[15px] text-foreground/80 leading-relaxed whitespace-pre-wrap break-words font-medium">
            {job.description}
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="shrink-0 p-4 sm:p-8 pb-safe sm:pb-8 border-t border-white/[0.08] bg-[#030305]/80 backdrop-blur-xl relative z-10">
        <JobCardActions jobId={job.id} jobUrl={job.url} isSaved={isSaved} />
      </div>
    </div>
  )
}
