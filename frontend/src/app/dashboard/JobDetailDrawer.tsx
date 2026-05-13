'use client'

import { useEffect } from 'react'
import { X, MapPin, Globe, Building2, ExternalLink, Tag, Clock } from 'lucide-react'
import { JobCardActions } from './JobCardActions'
import type { ScoredJob } from './useJobFilters'

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

export function JobDetailDrawer({ job, isSaved, onClose }: {
  job: ScoredJob | null; isSaved: boolean; onClose: () => void
}) {
  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (job) document.body.style.overflow = 'hidden'
    else document.body.style.overflow = ''
    return () => { document.body.style.overflow = '' }
  }, [job])

  if (!job) return null

  const initials = job.company.split(/\s+/).map(w => w[0]).join('').substring(0, 2).toUpperCase()

  return (
    <>
      {/* Backdrop (Mobile Only) */}
      <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[60] animate-fade-in lg:hidden" onClick={onClose} />
      
      {/* Container: Drawer on mobile, Static Pane on Desktop */}
      <div className="fixed right-0 top-0 bottom-0 w-full sm:max-w-[600px] lg:static lg:w-full lg:max-w-none lg:h-full lg:rounded-2xl bg-background lg:border border-border z-[70] lg:z-auto flex flex-col drawer-slide-in lg:animate-none overflow-hidden shadow-2xl lg:shadow-sm">
        {/* Header */}
        <div className="shrink-0 p-5 sm:p-6 lg:p-8 border-b border-border relative overflow-hidden bg-white">
          <div className="relative flex items-start justify-between mb-5">
            <div className="flex items-center gap-4 pr-8">
              <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-lg sm:text-xl font-bold shadow-md shrink-0">
                {initials}
              </div>
              <div>
                <h2 className="text-xl sm:text-2xl font-bold leading-tight tracking-tight mb-1">{job.title}</h2>
                <div className="flex flex-wrap items-center gap-2 text-[13px] sm:text-[14px] text-muted-foreground font-medium">
                  <div className="flex items-center gap-1.5 text-foreground/80">
                    <Building2 className="w-3.5 h-3.5" />
                    <span>{job.company}</span>
                  </div>
                  <span className="w-1 h-1 rounded-full bg-border hidden sm:block" />
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{timeAgo(job.created_at)}</span>
                  </div>
                </div>
              </div>
            </div>
            {/* Close button (only visible on mobile) */}
            <button onClick={onClose} className="absolute right-0 top-0 p-2 rounded-xl hover:bg-muted text-muted-foreground transition-all duration-200 lg:hidden">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Quick Info Chips */}
          <div className="flex flex-wrap gap-2 relative">
            {job.location && (
              <span className="chip">
                <MapPin className="w-3.5 h-3.5 opacity-70" />{job.location}
              </span>
            )}
            {job.remote && (
              <span className="chip text-blue-700 bg-blue-50 border-blue-200">
                <Globe className="w-3.5 h-3.5 opacity-70" />Remote
              </span>
            )}
            {job.salary && (
              <span className="chip text-emerald-700 bg-emerald-50 border-emerald-200">
                💰 {job.salary}
              </span>
            )}
            {job.job_type && (
              <span className="chip text-amber-700 bg-amber-50 border-amber-200">
                {job.job_type}
              </span>
            )}
            <span className="chip">
              Source: {job.source}
            </span>
          </div>
        </div>

        {/* Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 custom-scrollbar pb-24 sm:pb-8 bg-gray-50/50">
          {/* Tags */}
          {job.tags && job.tags.length > 0 && (
            <div>
              <h4 className="text-[11px] font-bold text-muted-foreground uppercase tracking-widest mb-3 flex items-center gap-2">
                <Tag className="w-3.5 h-3.5" /> Skills & Tags
              </h4>
              <div className="flex flex-wrap gap-2">
                {job.tags.map(tag => (
                  <span key={tag} className="chip">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          <div>
            <h4 className="text-[11px] font-bold text-muted-foreground uppercase tracking-widest mb-3 sm:mb-4 flex items-center gap-2">
              <ExternalLink className="w-3.5 h-3.5" /> Job Description
            </h4>
            <div className="text-[14px] sm:text-[15px] text-foreground/80 leading-relaxed whitespace-pre-wrap break-words">
              {job.description}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="shrink-0 p-4 sm:p-6 border-t border-border bg-white relative z-10">
          <JobCardActions jobId={job.id} jobUrl={job.url} isSaved={isSaved} />
        </div>
      </div>
    </>
  )
}
