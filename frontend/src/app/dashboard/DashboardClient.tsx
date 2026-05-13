'use client'

import { useState, useMemo, useCallback, useRef, useEffect } from 'react'
import { Briefcase, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useJobFilters, type Job, type FilterState, DEFAULT_FILTERS } from './useJobFilters'
import { HeroSearch } from './HeroSearch'
import { HorizontalJobCard } from './HorizontalJobCard'
import { JobDetailDrawer } from './JobDetailDrawer'
import { JobDetailPane } from './JobDetailPane'

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
    if (scrollRef.current) scrollRef.current.scrollTop = 0
  }, [filters])

  // Infinite scroll handler
  const handleScroll = useCallback(() => {
    if (!scrollRef.current || isLoadingMore || !hasMore) return
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current
    
    if (scrollHeight - scrollTop - clientHeight < 300) {
      setIsLoadingMore(true)
      setTimeout(() => {
        setVisibleCount(prev => prev + LOAD_MORE_COUNT)
        setIsLoadingMore(false)
      }, 100)
    }
  }, [isLoadingMore, hasMore])

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    el.addEventListener('scroll', handleScroll)
    return () => el.removeEventListener('scroll', handleScroll)
  }, [handleScroll])

  return (
    <div className="flex flex-col h-[calc(100dvh-64px)] w-full max-w-[1600px] mx-auto px-4 sm:px-6 py-4">
      {/* Top Search Area */}
      <div className="shrink-0 mb-6">
        <HeroSearch
          filters={filters}
          setFilters={(f) => {
            if (typeof f === 'function') setFilters(f)
            else setFilters(f)
          }}
          totalResults={filteredJobs.length}
        />
      </div>

      {/* Main Content Area - Split Pane */}
      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[400px_1fr] xl:grid-cols-[450px_1fr] gap-6 lg:gap-8 pb-4">
        
        {/* Left Column: Job List */}
        <div className="flex flex-col min-h-0 h-full">
          <div ref={scrollRef} className="flex-1 overflow-y-auto pr-3 space-y-4 pb-safe custom-scrollbar">
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

        {/* Right Column: Detail Pane (Desktop Only) */}
        <div className="hidden lg:flex flex-col min-h-0 h-full">
          {selectedJob ? (
            <JobDetailPane
              job={selectedJob as unknown as import('./useJobFilters').ScoredJob}
              isSaved={savedJobIds.has(selectedJob.id)}
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center border border-white/[0.04] rounded-2xl bg-[#09090b]/50">
              <Briefcase className="w-10 h-10 text-muted-foreground/20 mb-4" />
              <h3 className="text-lg font-semibold text-muted-foreground/60">Select a job</h3>
              <p className="text-sm text-muted-foreground/40 mt-1">
                Click a job on the left to view details
              </p>
            </div>
          )}
        </div>

      </div>

      {/* Job Detail Drawer (Mobile Only) */}
      <JobDetailDrawer
        job={selectedJob as unknown as import('./useJobFilters').ScoredJob}
        isSaved={selectedJob ? savedJobIds.has(selectedJob.id) : false}
        onClose={() => setSelectedJob(null)}
      />
    </div>
  )
}
