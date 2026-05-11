'use client'

import { Search, Globe, Filter, Calendar, MapPin, Database } from 'lucide-react'
import type { FilterState } from './useJobFilters'

interface Props {
  filters: FilterState
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>
  totalResults: number
  showMap: boolean
  setShowMap: (show: boolean) => void
}

export function DashboardFilters({ filters, setFilters, totalResults, showMap, setShowMap }: Props) {
  
  const handleSourceToggle = (source: string) => {
    setFilters(prev => {
      const isSelected = prev.sources.includes(source)
      return {
        ...prev,
        sources: isSelected 
          ? prev.sources.filter(s => s !== source)
          : [...prev.sources, source]
      }
    })
  }

  return (
    <div className="space-y-4">
      {/* Top Search Row */}
      <div className="flex gap-3 items-center flex-wrap sm:flex-nowrap">
        {/* Main strict AND search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <input
            type="text"
            placeholder="Strict search: e.g. 'python engineer'"
            value={filters.searchQuery}
            onChange={(e) => setFilters(f => ({ ...f, searchQuery: e.target.value }))}
            className="w-full h-10 pl-10 pr-4 rounded-xl glass-input text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:border-primary/50"
          />
        </div>

        {/* Remote toggle */}
        <button
          onClick={() => setFilters(f => ({ ...f, remoteOnly: !f.remoteOnly }))}
          className={`h-10 px-4 rounded-xl text-sm font-medium flex items-center gap-2 transition-all duration-200 shrink-0 ${
            filters.remoteOnly
              ? 'bg-primary/15 text-primary border border-primary/30'
              : 'glass text-muted-foreground hover:text-foreground'
          }`}
        >
          <Globe className="w-3.5 h-3.5" />
          Remote
        </button>

        {/* Map toggle */}
        <button
          onClick={() => setShowMap(!showMap)}
          className={`h-10 px-4 rounded-xl text-sm font-medium flex items-center gap-2 transition-all duration-200 shrink-0 ${
            showMap || filters.mapCenter
              ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
              : 'glass text-muted-foreground hover:text-foreground'
          }`}
        >
          <MapPin className="w-3.5 h-3.5" />
          {filters.mapCenter ? 'Map Filter Active' : 'Map'}
        </button>
      </div>

      {/* Advanced Filters Row */}
      <div className="flex flex-wrap items-center gap-4 p-3 rounded-xl glass-card border border-white/[0.04]">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider pr-2 border-r border-white/10">
          <Filter className="w-3.5 h-3.5" />
          Filters
        </div>

        {/* Date Filter */}
        <div className="flex items-center gap-2">
          <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
          <select 
            value={filters.datePosted}
            onChange={(e) => setFilters(f => ({ ...f, datePosted: e.target.value }))}
            className="bg-transparent text-sm text-foreground outline-none cursor-pointer focus:ring-0 [&>option]:bg-[#0a0a12]"
          >
            <option value="all">Any time</option>
            <option value="24h">Past 24 hours</option>
            <option value="7d">Past week</option>
            <option value="30d">Past month</option>
          </select>
        </div>

        {/* Source Filter */}
        <div className="flex items-center gap-3 pl-4 border-l border-white/10">
          <Database className="w-3.5 h-3.5 text-muted-foreground" />
          {['Arbeitnow', 'Hacker News', 'Remotive', 'Direct'].map(source => (
            <label key={source} className="flex items-center gap-1.5 cursor-pointer group">
              <input 
                type="checkbox"
                checked={filters.sources.includes(source)}
                onChange={() => handleSourceToggle(source)}
                className="w-3.5 h-3.5 rounded border-white/20 bg-white/5 text-primary focus:ring-primary/50 focus:ring-offset-0 cursor-pointer"
              />
              <span className="text-xs text-muted-foreground group-hover:text-foreground transition-colors">
                {source}
              </span>
            </label>
          ))}
        </div>

        {/* Map Radius Slider (only show if map center is set) */}
        {filters.mapCenter && (
          <div className="flex items-center gap-3 pl-4 border-l border-white/10 ml-auto">
            <span className="text-xs text-muted-foreground">Radius:</span>
            <input 
              type="range" 
              min="10" 
              max="500" 
              step="10"
              value={filters.mapRadiusKm || 100}
              onChange={(e) => setFilters(f => ({ ...f, mapRadiusKm: parseInt(e.target.value) }))}
              className="w-24 accent-primary"
            />
            <span className="text-xs font-medium w-12">{filters.mapRadiusKm} km</span>
          </div>
        )}
      </div>

      {/* Results status */}
      <div className="text-xs text-muted-foreground px-1">
        Showing <span className="font-semibold text-foreground">{totalResults}</span> results matching all criteria
      </div>
    </div>
  )
}
