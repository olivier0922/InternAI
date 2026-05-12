'use client'

import { useState, useEffect } from 'react'
import { Search, Globe, X, Briefcase, Calendar, MapPin } from 'lucide-react'
import type { FilterState } from './useJobFilters'
import { DEFAULT_FILTERS } from './useJobFilters'

interface Props {
  filters: FilterState
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>
  totalResults: number
}

const POPULAR_SEARCHES = ['Software Engineer', 'Frontend', 'Backend', 'Full Stack', 'Machine Learning', 'Data Scientist', 'DevOps', 'Cybersecurity', 'Intern', 'New Grad']
const DATE_OPTIONS = [
  { value: 'all', label: 'Any time' },
  { value: '24h', label: '24h' },
  { value: '7d', label: 'Week' },
  { value: '30d', label: 'Month' },
]

export function HeroSearch({ filters, setFilters, totalResults }: Props) {
  const [localWhat, setLocalWhat] = useState(filters.searchQuery)
  const [localWhere, setLocalWhere] = useState(filters.locationQuery)

  useEffect(() => {
    const timeout = setTimeout(() => {
      setFilters(prev => {
        if (prev.searchQuery === localWhat && prev.locationQuery === localWhere) return prev
        return { ...prev, searchQuery: localWhat, locationQuery: localWhere }
      })
    }, 300)
    return () => clearTimeout(timeout)
  }, [localWhat, localWhere, setFilters])

  const hasActiveFilters = filters.remoteOnly || filters.datePosted !== 'all' || filters.sources.length > 0 || localWhat || localWhere

  const clearAllFilters = () => {
    setLocalWhat('')
    setLocalWhere('')
    setFilters(DEFAULT_FILTERS)
  }

  return (
    <div className="w-full space-y-4">
      {/* Premium Search Bar */}
      <div className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/30 to-fuchsia-500/30 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-500"></div>
        <div className="relative flex flex-col md:flex-row bg-[#0c0c16]/80 backdrop-blur-xl rounded-2xl border border-white/[0.1] shadow-2xl overflow-hidden glass-card">
          
          {/* What Input */}
          <div className="flex-1 relative flex items-center border-b md:border-b-0 md:border-r border-white/[0.08]">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-[22px] w-[22px] text-primary/70" />
            <input type="text" placeholder="Job title, company, or skill..." value={localWhat} onChange={(e) => setLocalWhat(e.target.value)}
              className="w-full h-[60px] pl-[52px] pr-4 bg-transparent text-[16px] font-medium placeholder:text-muted-foreground/60 focus:outline-none focus:bg-white/[0.03] transition-colors" />
            {localWhat && <button onClick={() => setLocalWhat('')} className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg hover:bg-white/[0.08] transition-colors"><X className="w-4 h-4 text-muted-foreground hover:text-foreground" /></button>}
          </div>

          {/* Where Input */}
          <div className="flex-1 relative flex items-center">
            <MapPin className="absolute left-5 top-1/2 -translate-y-1/2 h-[22px] w-[22px] text-primary/70" />
            <input type="text" placeholder="City, state, or zip..." value={localWhere} onChange={(e) => setLocalWhere(e.target.value)}
              className="w-full h-[60px] pl-[52px] pr-4 bg-transparent text-[16px] font-medium placeholder:text-muted-foreground/60 focus:outline-none focus:bg-white/[0.03] transition-colors" />
            {localWhere && <button onClick={() => setLocalWhere('')} className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg hover:bg-white/[0.08] transition-colors"><X className="w-4 h-4 text-muted-foreground hover:text-foreground" /></button>}
          </div>

          <button onClick={() => setFilters(f => ({ ...f, remoteOnly: !f.remoteOnly }))}
            className={`h-[60px] px-8 font-bold flex items-center justify-center gap-2.5 transition-all duration-300 shrink-0 md:border-l border-white/[0.08] ${filters.remoteOnly ? 'gradient-btn text-white' : 'bg-transparent text-muted-foreground hover:text-foreground hover:bg-white/[0.05]'}`}>
            <Globe className={`w-5 h-5 ${filters.remoteOnly ? 'text-white' : 'text-primary/70'}`} />Remote
          </button>
        </div>
      </div>

      {/* Quick Search Suggestions (only when no search query) */}
      {!localWhat && (
        <div className="flex items-center gap-2 px-2 flex-wrap animate-fade-in">
          <span className="text-[11px] font-bold text-muted-foreground/60 uppercase tracking-wider mr-1">Trending</span>
          {POPULAR_SEARCHES.map(term => (
            <button key={term} onClick={() => setLocalWhat(term)}
              className="text-[11px] font-semibold px-3 py-1.5 rounded-full bg-white/[0.02] border border-white/[0.08] text-muted-foreground hover:text-foreground hover:bg-white/[0.08] hover:border-primary/30 transition-all duration-200">
              {term}
            </button>
          ))}
        </div>
      )}

      {/* Filter Bar */}
      <div className="flex items-center gap-4 px-2 flex-wrap">
        {/* Date Filter Chips */}
        <div className="flex items-center gap-1.5">
          <div className="w-6 h-6 rounded-md bg-white/[0.04] flex items-center justify-center border border-white/[0.08] mr-1">
            <Calendar className="w-3.5 h-3.5 text-primary/80" />
          </div>
          {DATE_OPTIONS.map(opt => (
            <button key={opt.value} onClick={() => setFilters(f => ({ ...f, datePosted: opt.value }))}
              className={`text-[12px] font-medium px-3 py-1.5 rounded-lg transition-all duration-200 ${
                filters.datePosted === opt.value
                  ? 'bg-primary/20 text-primary border border-primary/40 shadow-[0_0_10px_rgba(99,102,241,0.2)]'
                  : 'bg-transparent text-muted-foreground border border-transparent hover:text-foreground hover:bg-white/[0.05]'
              }`}>
              {opt.label}
            </button>
          ))}
        </div>

        {/* Results + Clear */}
        <div className="flex items-center gap-3 ml-auto">
          {hasActiveFilters && (
            <button onClick={clearAllFilters} className="text-[12px] font-semibold px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 hover:text-red-300 transition-all duration-200 flex items-center gap-1.5">
              <X className="w-3.5 h-3.5" />Reset
            </button>
          )}
          <div className="px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/[0.08]">
            <span className="text-[12px] font-medium text-muted-foreground">
              <span className="text-foreground font-bold">{totalResults.toLocaleString()}</span> jobs
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
