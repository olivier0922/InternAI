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
    <div className="w-full space-y-3">
      {/* Command Palette Search Bar */}
      <div className="relative group">
        <div className="relative flex flex-col md:flex-row bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden transition-all focus-within:border-blue-300 focus-within:ring-4 focus-within:ring-blue-500/10 hover:border-gray-300">
          
          {/* What Input */}
          <div className="flex-1 relative flex items-center border-b md:border-b-0 md:border-r border-gray-100">
            <Search className="absolute left-4 h-4 w-4 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
            <input type="text" placeholder="Job title, company, or skill..." value={localWhat} onChange={(e) => setLocalWhat(e.target.value)}
              className="w-full h-11 md:h-12 pl-10 pr-4 bg-transparent text-sm font-medium placeholder:text-gray-400 focus:outline-none" />
            {localWhat && <button onClick={() => setLocalWhat('')} className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-md hover:bg-gray-100"><X className="w-3.5 h-3.5 text-gray-400" /></button>}
          </div>

          {/* Where Input */}
          <div className="flex-1 relative flex items-center border-b md:border-b-0 border-gray-100">
            <MapPin className="absolute left-4 h-4 w-4 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
            <input type="text" placeholder="City, state, or zip..." value={localWhere} onChange={(e) => setLocalWhere(e.target.value)}
              className="w-full h-11 md:h-12 pl-10 pr-4 bg-transparent text-sm font-medium placeholder:text-gray-400 focus:outline-none" />
            {localWhere && <button onClick={() => setLocalWhere('')} className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-md hover:bg-gray-100"><X className="w-3.5 h-3.5 text-gray-400" /></button>}
          </div>

          <button onClick={() => setFilters(f => ({ ...f, remoteOnly: !f.remoteOnly }))}
            className={`h-11 md:h-12 px-6 font-semibold flex items-center justify-center gap-2 transition-all duration-200 shrink-0 md:border-l border-gray-100 text-sm ${filters.remoteOnly ? 'bg-blue-50 text-blue-700 hover:bg-blue-100' : 'bg-transparent text-gray-500 hover:text-gray-900 hover:bg-gray-50'}`}>
            <Globe className={`w-4 h-4 ${filters.remoteOnly ? 'text-blue-600' : 'text-gray-400'}`} />Remote
          </button>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-1">
        {/* Quick Search Suggestions & Filters */}
        <div className="flex items-center gap-2 overflow-x-auto whitespace-nowrap custom-scrollbar pb-1 sm:pb-0 -mb-1 sm:mb-0">
          {!localWhat && (
            <>
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mr-1">Trending</span>
              {POPULAR_SEARCHES.slice(0, 5).map(term => (
                <button key={term} onClick={() => setLocalWhat(term)}
                  className="text-xs font-medium px-2.5 py-1 rounded-md bg-white border border-gray-200 text-gray-600 hover:text-gray-900 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 shrink-0">
                  {term}
                </button>
              ))}
              <div className="w-px h-4 bg-gray-200 mx-1"></div>
            </>
          )}

          {/* Date Filter Chips */}
          <div className="flex items-center gap-1.5">
            <div className="w-6 h-6 shrink-0 flex items-center justify-center">
              <Calendar className="w-3.5 h-3.5 text-gray-400" />
            </div>
            {DATE_OPTIONS.map(opt => (
              <button key={opt.value} onClick={() => setFilters(f => ({ ...f, datePosted: opt.value }))}
                className={`text-[11px] font-semibold px-2.5 py-1 rounded-md transition-all duration-200 shrink-0 border ${
                  filters.datePosted === opt.value
                    ? 'bg-blue-50 text-blue-700 border-blue-200 shadow-sm'
                    : 'bg-white text-gray-500 border-gray-200 hover:text-gray-900 hover:bg-gray-50'
                }`}>
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Results + Clear */}
        <div className="flex items-center gap-3 shrink-0">
          {hasActiveFilters && (
            <button onClick={clearAllFilters} className="text-[11px] font-semibold px-2.5 py-1 rounded-md bg-red-50 text-red-600 border border-red-100 hover:bg-red-100 transition-all duration-200 flex items-center gap-1">
              <X className="w-3 h-3" />Reset
            </button>
          )}
          <div className="px-2.5 py-1 rounded-md bg-gray-50 border border-gray-200">
            <span className="text-[11px] font-medium text-gray-500">
              <span className="text-gray-900 font-bold">{totalResults.toLocaleString()}</span> jobs
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
