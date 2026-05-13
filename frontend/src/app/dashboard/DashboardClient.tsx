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
    <div className="flex flex-col h-[calc(100vh-140px)] lg:h-[calc(100vh-64px)] w-full max-w-[1600px] mx-auto overflow-hidden">
      {/* Top Search Area */}
      <div className="shrink-0 mb-4 mt-2 px-4 lg:px-0">
        <HeroSearch
          filters={filters}
          setFilters={(f) => {
            if (typeof f === 'function') setFilters(f)
            else setFilters(f)
          }}
          totalResults={filteredJobs.length}
        />
      </div>

      {/* Split-Pane Content Area */}
      <div className="flex-1 min-h-0 flex lg:gap-6 px-4 lg:px-0 pb-4">
        
        {/* Left Pane: Job List */}
        <div className="w-full lg:w-[45%] xl:w-[40%] flex-shrink-0 h-full overflow-hidden flex flex-col">
          <div ref={scrollRef} className="h-full overflow-y-auto pr-2 custom-scrollbar space-y-3 pb-6">
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
                      <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                    ) : (
                      <span className="text-xs text-gray-400">
                        Showing {visibleJobs.length} of {filteredJobs.length} · Scroll for more
                      </span>
                    )}
                  </div>
                )}
                {!hasMore && filteredJobs.length > JOBS_PER_PAGE && (
                  <div className="flex items-center justify-center py-4">
                    <span className="text-xs text-gray-400">All {filteredJobs.length} results loaded</span>
                  </div>
                )}
              </>
            ) : (
              <div className="flex flex-col items-center justify-center py-32 text-center bg-white rounded-2xl border border-dashed border-gray-200">
                <div className="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
                  <Briefcase className="w-7 h-7 text-gray-400" />
                </div>
                <h3 className="text-base font-semibold text-gray-900 mb-1">No jobs match your search</h3>
                <p className="text-sm text-gray-500 max-w-sm mb-4">
                  Try adjusting your search terms, expanding filters, or checking different sources.
                </p>
                <button
                  onClick={() => setFilters(DEFAULT_FILTERS)}
                  className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Right Pane: Job Details (Desktop Only) */}
        <div className="hidden lg:flex flex-1 h-full overflow-hidden">
          {selectedJob ? (
            <JobDetailDrawer
              job={selectedJob as unknown as import('./useJobFilters').ScoredJob}
              isSaved={savedJobIds.has(selectedJob.id)}
              onClose={() => setSelectedJob(null)}
            />
          ) : (
            <div className="w-full h-full rounded-2xl border border-gray-200 bg-gray-50/50 flex flex-col items-center justify-center text-center p-8">
              <div className="w-16 h-16 rounded-full bg-white border border-gray-200 shadow-sm flex items-center justify-center mb-4">
                <Briefcase className="w-8 h-8 text-gray-300" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Select a job</h3>
              <p className="text-sm text-gray-500 max-w-sm">
                Click on any job card from the list to view its full description, required skills, and application options here.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Drawer (Hidden on LG screens) */}
      <div className="lg:hidden">
        <JobDetailDrawer
          job={selectedJob as unknown as import('./useJobFilters').ScoredJob}
          isSaved={selectedJob ? savedJobIds.has(selectedJob.id) : false}
          onClose={() => setSelectedJob(null)}
        />
      </div>
    </div>
  )
}
