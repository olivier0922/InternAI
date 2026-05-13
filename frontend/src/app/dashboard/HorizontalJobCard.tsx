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
      <div className="relative glass-card rounded-2xl p-4 sm:p-5 flex flex-col gap-3 transition-all duration-300">
        
        {/* Header: Avatar + Title */}
        <div className="flex items-start gap-3.5">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${companyColor(job.company)} flex items-center justify-center text-white text-base font-bold shrink-0 shadow-md border border-white/5 relative overflow-hidden group-hover:scale-105 transition-transform duration-300`}>
            <div className="absolute inset-0 bg-black/10 group-hover:bg-transparent transition-colors duration-300" />
            <span className="relative z-10">{initials}</span>
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold text-[16px] leading-snug group-hover:text-primary transition-colors line-clamp-2 tracking-tight">
                {job.title}
              </h3>
              <div className="flex flex-col items-end gap-1 shrink-0">
                <span className="text-[11px] font-medium text-muted-foreground/60 whitespace-nowrap">
                  {timeAgo(job.created_at)}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2 text-[13px] text-muted-foreground mt-0.5 line-clamp-1">
              <Building2 className="w-3.5 h-3.5 shrink-0" />
              <span className="truncate">{job.company}</span>
            </div>
          </div>
        </div>

        {/* Badges / Source */}
        <div className="flex flex-wrap items-center gap-2 mt-1">
          <span className={`text-[10px] font-medium px-2 py-0.5 rounded border uppercase tracking-wider ${sourceColor(job.source)}`}>
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

        {/* Description Snippet */}
        <p className="text-[13px] text-muted-foreground leading-relaxed line-clamp-2 mt-1">
          {job.description}
        </p>

        {/* Chips */}
        <div className="flex flex-wrap items-center gap-1.5 mt-2">
          {job.location && (
            <span className="chip text-[11px] px-2 py-1">
              <MapPin className="w-3 h-3 opacity-70" />
              {job.location.length > 20 ? job.location.substring(0, 20) + '…' : job.location}
            </span>
          )}
          {job.remote && (
            <span className="chip text-[11px] px-2 py-1 text-indigo-300 border-indigo-500/20 bg-indigo-500/10">
              <Globe className="w-3 h-3 opacity-70" />Remote
            </span>
          )}
          {job.salary && (
            <span className="chip text-[11px] px-2 py-1 text-emerald-400 border-emerald-500/20 bg-emerald-500/10">
              💰 {job.salary.length > 20 ? job.salary.substring(0, 20) + '…' : job.salary}
            </span>
          )}
          {job.tags?.slice(0, 2).map(tag => (
            <span key={tag} className="chip text-[11px] px-2 py-1 hidden sm:inline-flex">
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
