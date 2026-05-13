'use client'

import { MapPin, Globe, Building2, Clock, Sparkles, Tag } from 'lucide-react'
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

function companyColor(name: string): string {
  const colors = [
    'from-indigo-500 to-purple-600', 'from-emerald-500 to-teal-600',
    'from-amber-500 to-orange-600', 'from-rose-500 to-pink-600',
    'from-cyan-500 to-blue-600', 'from-violet-500 to-indigo-600',
    'from-lime-500 to-green-600', 'from-fuchsia-500 to-pink-600',
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

function sourceColor(source: string): string {
  const map: Record<string, string> = {
    'Remotive': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    'Arbeitnow': 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    'FindWork': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    'Hacker News': 'bg-orange-600/10 text-orange-300 border-orange-600/20',
    'Jobicy': 'bg-teal-500/10 text-teal-400 border-teal-500/20',
    'The Muse': 'bg-pink-500/10 text-pink-400 border-pink-500/20',
    'Himalayas': 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    'Direct': 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  }
  return map[source] || 'bg-white/5 text-muted-foreground border-white/10'
}

export function HorizontalJobCard({ job, onClick }: {
  job: ScoredJob; onClick?: () => void
}) {
  const isNew = Date.now() - new Date(job.created_at).getTime() < 86400000
  const showMatch = job.relevanceScore >= 15
  const initials = job.company.split(/\s+/).map(w => w[0]).join('').substring(0, 2).toUpperCase()

  return (
    <div onClick={onClick} className="relative group cursor-pointer block">
      <div className="relative glass-card rounded-2xl p-4 sm:p-5 md:p-6 flex flex-col md:flex-row gap-4 sm:gap-5 transition-all duration-300">
        
        {/* Company Logo / Avatar & Mobile Header container */}
        <div className="flex items-start gap-4 md:shrink-0">
          <div className={`w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-gradient-to-br ${companyColor(job.company)} flex items-center justify-center text-white text-base sm:text-lg font-bold shrink-0 shadow-md border border-white/5 relative overflow-hidden group-hover:scale-105 transition-transform duration-300`}>
            <div className="absolute inset-0 bg-black/10 group-hover:bg-transparent transition-colors duration-300" />
            <span className="relative z-10">{initials}</span>
          </div>
          
          {/* Mobile Title (shows only on small screens) */}
          <div className="md:hidden flex-1 min-w-0">
            <h3 className="font-semibold text-[16px] sm:text-[18px] leading-snug group-hover:text-primary transition-colors line-clamp-2 tracking-tight">
              {job.title}
            </h3>
            <div className="flex items-center gap-2 text-[13px] text-muted-foreground mt-1">
              <span className="truncate">{job.company}</span>
              <span className="w-1 h-1 rounded-full bg-white/10 shrink-0" />
              <span className="shrink-0">{timeAgo(job.created_at)}</span>
            </div>
          </div>
        </div>

        <div className="flex-1 min-w-0 flex flex-col justify-between">
          <div>
            <div className="hidden md:flex items-start justify-between gap-3 mb-1.5">
              <h3 className="font-semibold text-[17px] sm:text-[19px] leading-snug group-hover:text-primary transition-colors line-clamp-1 tracking-tight">
                {job.title}
              </h3>
              <div className="flex items-center gap-2 shrink-0 pt-0.5">
                {showMatch && (
                  <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded bg-primary/10 text-primary border border-primary/20 uppercase tracking-widest">
                    <Sparkles className="w-3 h-3" />Match
                  </span>
                )}
                {isNew && !showMatch && (
                  <span className="text-[10px] font-bold px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-widest">
                    New
                  </span>
                )}
              </div>
            </div>

            <div className="hidden md:flex items-center gap-2.5 text-[13px] sm:text-sm text-muted-foreground mb-3">
              <div className="flex items-center gap-1.5 text-foreground/80 font-medium">
                <Building2 className="w-4 h-4 text-muted-foreground" />
                {job.company}
              </div>
              <span className="w-1 h-1 rounded-full bg-white/10" />
              <span className={`text-[11px] font-medium px-2 py-0.5 rounded border ${sourceColor(job.source)}`}>
                {job.source}
              </span>
            </div>

            {/* Mobile Badges (shows only on small screens) */}
            <div className="md:hidden flex items-center gap-2 mb-3">
              <span className={`text-[11px] font-medium px-2 py-0.5 rounded border ${sourceColor(job.source)}`}>
                {job.source}
              </span>
              {showMatch && (
                  <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20 uppercase tracking-widest">
                    <Sparkles className="w-2.5 h-2.5" />Match
                  </span>
              )}
              {isNew && !showMatch && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-widest">
                    New
                  </span>
              )}
            </div>

            <p className="text-[13px] text-muted-foreground leading-relaxed mb-4 max-w-3xl line-clamp-2">
              {job.description}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 mt-auto">
            {job.location && (
              <span className="chip">
                <MapPin className="w-3.5 h-3.5 opacity-70" />
                {job.location.length > 30 ? job.location.substring(0, 30) + '…' : job.location}
              </span>
            )}
            {job.remote && (
              <span className="chip text-indigo-300 border-indigo-500/20 bg-indigo-500/10">
                <Globe className="w-3 h-3 opacity-70" />Remote
              </span>
            )}
            {job.salary && (
              <span className="chip text-emerald-400 border-emerald-500/20 bg-emerald-500/10">
                💰 {job.salary.length > 30 ? job.salary.substring(0, 30) + '…' : job.salary}
              </span>
            )}
            {job.job_type && job.job_type !== 'Full-time' && (
              <span className="chip text-amber-300 border-amber-500/20 bg-amber-500/10">
                {job.job_type}
              </span>
            )}
            {job.tags?.slice(0, 3).map(tag => (
              <span key={tag} className="chip">
                <Tag className="w-2.5 h-2.5 opacity-50" />{tag}
              </span>
            ))}
            
            <span className="hidden md:flex text-[11px] font-medium text-muted-foreground/40 items-center gap-1 ml-auto">
              <Clock className="w-3 h-3" />
              {timeAgo(job.created_at)}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
