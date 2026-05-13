import { useEffect } from 'react'
import { X } from 'lucide-react'
import type { ScoredJob } from './useJobFilters'
import { JobDetailPane } from './JobDetailPane'

export function JobDetailDrawer({ job, isSaved, onClose }: {
  job: ScoredJob | null; isSaved: boolean; onClose: () => void
}) {
  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  // Prevent body scroll when drawer is open (only on mobile)
  useEffect(() => {
    if (job && window.innerWidth < 1024) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [job])

  if (!job) return null

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[60] animate-fade-in lg:hidden" onClick={onClose} />
      
      {/* Drawer Container */}
      <div className="fixed right-0 top-0 bottom-0 w-full sm:max-w-[600px] z-[70] flex flex-col drawer-slide-in shadow-[0_0_50px_rgba(0,0,0,0.5)] lg:hidden bg-background">
        <button 
          onClick={onClose} 
          className="absolute right-4 top-4 p-2 z-[80] rounded-xl hover:bg-white/[0.08] text-muted-foreground hover:text-foreground transition-all duration-200 backdrop-blur-md bg-white/[0.02] border border-white/[0.05]"
        >
          <X className="w-5 h-5" />
        </button>
        <div className="flex-1 h-full pt-14">
          <JobDetailPane job={job} isSaved={isSaved} />
        </div>
      </div>
    </>
  )
}
