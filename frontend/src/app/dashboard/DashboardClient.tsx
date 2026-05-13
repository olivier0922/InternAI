'use client'

import { useState, useMemo, useCallback, useRef, useEffect } from 'react'
import { Briefcase, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useJobFilters, type Job, type FilterState, DEFAULT_FILTERS } from './useJobFilters'
import { HeroSearch } from './HeroSearch'
import { HorizontalJobCard } from './HorizontalJobCard'
import { JobDetailDrawer } from './JobDetailDrawer'

const JOBS_PER_PAGE = 30
const LOAD_MORE_COUNT = 20

export function DashboardClient({ initialJobs, savedJobIds, userSkills }: { initialJobs: Job[]; savedJobIds: Set<string>; userSkills: string[] }) {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS)
  const [visibleCount, setVisibleCount] = useState(JOBS_PER_PAGE)
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  const filteredJobs = useJobFilters(initialJobs, filters, userSkills)

  const visibleJobs = useMemo(() => filteredJobs.slice(0, visibleCount), [filteredJobs, visibleCount])
  const hasMore = visibleCount < filteredJobs.length

  // Reset visible count when filters change
  useEffect(() => {
    setVisibleCount(JOBS_PER_PAGE)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [filters])

  // Infinite scroll handler
  const handleScroll = useCallback(() => {
    if (isLoadingMore || !hasMore) return
    
    const scrollTop = window.scrollY || document.documentElement.scrollTop
    const scrollHeight = document.documentElement.scrollHeight
    const clientHeight = window.innerHeight

    if (scrollHeight - scrollTop - clientHeight < 300) {
      setIsLoadingMore(true)
      setTimeout(() => {
        setVisibleCount(prev => prev + LOAD_MORE_COUNT)
        setIsLoadingMore(false)
      }, 100)
    }
  }, [isLoadingMore, hasMore])

  useEffect(() => {
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [handleScroll])

  return (
    <div className="flex flex-col min-h-[calc(100dvh-64px)] w-full max-w-3xl mx-auto px-4 sm:px-6">
      {/* Top Search Area */}
      <div className="shrink-0 mb-4 sm:mb-5 mt-2">
        <HeroSearch
          filters={filters}
          setFilters={(f) => {
            if (typeof f === 'function') setFilters(f)
            else setFilters(f)
          }}
          totalResults={filteredJobs.length}
        />
      </div>

      {/* Job List */}
      <div className="flex-1 min-h-0 mb-6">
        <div ref={scrollRef} className="h-full pr-2 space-y-3 pb-safe">
          {visibleJobs.length > 0 ? (
            <>
              <AnimatePresence mode="popLayout">
                {visibleJobs.map((job) => (
                  <motion.div
                    key={job.id}
                    layout
                    initial={{ opacity: 0, y: 20, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                  >
                    <HorizontalJobCard
                      job={job}
                      onClick={() => setSelectedJob(job)}
                    />
                  </motion.div>
                ))}
              </AnimatePresence>
              {/* Load more indicator */}
              {hasMore && (
                <div className="flex items-center justify-center py-6">
                  {isLoadingMore ? (
                    <Loader2 className="w-5 h-5 text-primary animate-spin" />
                  ) : (
                    <span className="text-xs text-muted-foreground/50">
                      Showing {visibleJobs.length} of {filteredJobs.length} · Scroll for more
                    </span>
                  )}
                </div>
              )}
              {!hasMore && filteredJobs.length > JOBS_PER_PAGE && (
                <div className="flex items-center justify-center py-4">
                  <span className="text-xs text-muted-foreground/40">All {filteredJobs.length} results loaded</span>
                </div>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 text-center glass-card rounded-2xl border-dashed">
              <div className="w-14 h-14 rounded-2xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center mb-4">
                <Briefcase className="w-7 h-7 text-muted-foreground/50" />
              </div>
              <h3 className="text-base font-semibold mb-1">No jobs match your search</h3>
              <p className="text-sm text-muted-foreground max-w-sm mb-4">
                Try adjusting your search terms, expanding filters, or checking different sources.
              </p>
              <button
                onClick={() => setFilters(DEFAULT_FILTERS)}
                className="px-4 py-2 rounded-lg text-sm font-medium glass hover:bg-white/5 transition-colors"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Job Detail Drawer */}
      <JobDetailDrawer
        job={selectedJob as unknown as import('./useJobFilters').ScoredJob}
        isSaved={selectedJob ? savedJobIds.has(selectedJob.id) : false}
        onClose={() => setSelectedJob(null)}
      />
    </div>
  )
}
