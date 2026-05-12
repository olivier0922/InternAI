'use client'

import { useState } from 'react'

import { Brain, Bookmark, ExternalLink, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'
import Link from 'next/link'

export function JobCardActions({ jobId, jobUrl, isSaved: initialSaved = false }: { jobId: string, jobUrl: string, isSaved?: boolean }) {
  const [loadingAI, setLoadingAI] = useState(false)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [matchData, setMatchData] = useState<any>(null)
  const [saved, setSaved] = useState(initialSaved)
  const supabase = createClient()

  const saveApplication = async (status: string) => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return

    const { data: existing } = await supabase
      .from('applications')
      .select('id')
      .eq('job_id', jobId)
      .eq('user_id', user.id)
      .single()

    if (existing) {
      await supabase.from('applications').update({ status }).eq('id', existing.id)
    } else {
      await supabase.from('applications').insert({ user_id: user.id, job_id: jobId, status })
    }
  }

  const handleSave = async () => {
    setSaved(true)
    await saveApplication('Saved')
  }

  const handleAI = async () => {
    setLoadingAI(true)
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/v1/ai/match`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ job_id: jobId })
      })

      if (!res.ok) {
        const err = await res.json()
        alert(err.detail || 'Upload a resume first to use AI Match.')
        setLoadingAI(false)
        return
      }

      const data = await res.json()
      setMatchData(data)
    } catch {
      alert("Failed to connect to AI service.")
    }
    setLoadingAI(false)
  }

  return (
    <div className="space-y-2.5 mt-auto pt-3 border-t border-white/[0.05]">
      {/* AI Match Result */}
      {matchData && (
        <div className="p-3 rounded-lg bg-primary/[0.05] border border-primary/[0.12] space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-primary">
              {matchData.score}% Match
            </span>
            {/* Score bar */}
            <div className="w-20 h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-primary to-violet-400 transition-all duration-500"
                style={{ width: `${matchData.score}%` }}
              />
            </div>
          </div>
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            {matchData.explanation}
          </p>
          <div className="flex flex-wrap gap-1">
            {matchData.matching_skills?.map((s: string) => (
              <span key={s} className="inline-flex items-center gap-0.5 text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/15">
                <CheckCircle2 className="w-2 h-2" />{s}
              </span>
            ))}
            {matchData.missing_skills?.map((s: string) => (
              <span key={s} className="inline-flex items-center gap-0.5 text-[10px] px-1.5 py-0.5 rounded bg-red-500/8 text-red-400 border border-red-500/15">
                <AlertCircle className="w-2 h-2" />{s}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-1.5">
        <button
          onClick={handleSave}
          disabled={saved}
          className={`flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg text-[11px] font-medium transition-all ${
            saved
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/15'
              : 'bg-white/[0.03] border border-white/[0.06] text-muted-foreground hover:text-foreground hover:bg-white/[0.06]'
          }`}
        >
          <Bookmark className={`w-3 h-3 ${saved ? 'fill-emerald-400' : ''}`} />
          {saved ? 'Saved' : 'Save'}
        </button>

        <button
          onClick={handleAI}
          disabled={loadingAI}
          className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg text-[11px] font-medium bg-primary/8 text-primary border border-primary/15 hover:bg-primary/12 transition-all disabled:opacity-50"
        >
          {loadingAI ? (
            <Loader2 className="w-3 h-3 animate-spin" />
          ) : (
            <Brain className="w-3 h-3" />
          )}
          {loadingAI ? 'Matching…' : 'AI Match'}
        </button>

        <Link href={jobUrl} target="_blank" onClick={() => saveApplication('Applied')} className="flex-1">
          <button className="w-full flex items-center justify-center gap-1 py-1.5 rounded-lg text-[11px] font-medium gradient-btn text-white">
            Apply <ExternalLink className="w-2.5 h-2.5" />
          </button>
        </Link>
      </div>
    </div>
  )
}
