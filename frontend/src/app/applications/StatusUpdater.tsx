'use client'

import { useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'


export function StatusUpdater({ appId, currentStatus }: { appId: string, currentStatus: string }) {
  const [isPending, setIsPending] = useState(false)
  const supabase = createClient()

  const handleUpdate = async (val: string | null) => {
    if (!val) return
    setIsPending(true)
    await supabase.from('applications').update({ status: val }).eq('id', appId)
    setIsPending(false)
    // To refresh the list, we trigger a soft refresh
    window.location.reload()
  }

  return (
    <Select
      defaultValue={currentStatus}
      onValueChange={handleUpdate}
      disabled={isPending}
    >
      <SelectTrigger className="h-8 text-xs w-full bg-white/[0.04] border-white/[0.08] shadow-none focus:ring-primary/30 rounded-lg">
        <SelectValue placeholder="Move to..." />
      </SelectTrigger>
      <SelectContent className="bg-[#1a1a2e] border-white/[0.1]">
        <SelectItem value="Saved">Saved</SelectItem>
        <SelectItem value="Applied">Applied</SelectItem>
        <SelectItem value="Interview">Interview</SelectItem>
        <SelectItem value="Offer">Offer</SelectItem>
        <SelectItem value="Rejected">Rejected</SelectItem>
      </SelectContent>
    </Select>
  )
}
