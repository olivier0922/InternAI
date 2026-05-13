'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { Building2, Loader2 } from 'lucide-react'
import { StatusUpdater } from './StatusUpdater'

export default function ApplicationsPage() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [applications, setApplications] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    let mounted = true
    const fetchData = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return

      const { data } = await supabase
        .from('applications')
        .select('*, jobs(*)')
        .eq('user_id', user.id)
        .order('applied_at', { ascending: false })

      if (mounted) {
        setApplications(data || [])
        setLoading(false)
      }
    }
    fetchData()
    return () => { mounted = false }
  }, [supabase])

  const columns = [
    { key: 'Saved', color: 'from-slate-400 to-slate-500' },
    { key: 'Applied', color: 'from-indigo-400 to-violet-500' },
    { key: 'Interview', color: 'from-amber-400 to-orange-500' },
    { key: 'Offer', color: 'from-emerald-400 to-green-500' },
    { key: 'Rejected', color: 'from-red-400 to-rose-500' },
  ]

  if (loading) {
    return (
      <div className="min-h-[calc(100dvh-64px)] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100dvh-64px)] p-4 sm:p-6 lg:p-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Applications</h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Track your job search pipeline · {applications?.length || 0} total
          </p>
        </div>

        {/* Kanban board */}
        <div className="flex gap-4 overflow-x-auto pb-4 items-start snap-x snap-mandatory custom-scrollbar">
          {columns.map(({ key: status, color }) => {
            const columnApps = applications?.filter(app => app.status === status) || []
            return (
              <div key={status} className="flex-1 min-w-[85vw] sm:min-w-[260px] snap-center space-y-3">
                {/* Column header */}
                <div className="flex items-center justify-between px-1 mb-1">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${color}`} />
                    <h3 className="font-semibold text-sm">{status}</h3>
                  </div>
                  <span className="text-xs text-muted-foreground bg-white/[0.06] px-2 py-0.5 rounded-full">
                    {columnApps.length}
                  </span>
                </div>

                {/* Cards container */}
                <div className="space-y-2">
                  {columnApps.map((app, index) => (
                    <div
                      key={app.id}
                      className="glass-card rounded-xl p-4 animate-fade-in"
                      style={{ animationDelay: `${index * 0.05}s` }}
                    >
                      <h4 className="text-sm font-medium leading-snug line-clamp-2 mb-1.5">
                        {app.jobs?.title}
                      </h4>
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-3">
                        <Building2 className="w-3 h-3" />
                        {app.jobs?.company}
                      </div>
                      <div className="pt-2 border-t border-white/[0.06]">
                        <StatusUpdater appId={app.id} currentStatus={app.status} />
                      </div>
                    </div>
                  ))}

                  {columnApps.length === 0 && (
                    <div className="flex items-center justify-center py-12 text-xs text-muted-foreground border border-dashed border-white/[0.08] rounded-xl bg-white/[0.01]">
                      No applications
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
