'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { Loader2 } from 'lucide-react'

export default function AuthCallbackPage() {
  const router = useRouter()
  const supabase = createClient()

  useEffect(() => {
    // Supabase automatically detects the #access_token in the URL hash 
    // and stores it in local storage when using the browser client.
    // We just wait for the session to be established and redirect.
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (session) {
        router.push('/dashboard')
      } else {
        // Give it a moment to process the hash
        setTimeout(async () => {
          const { data: { session: retrySession } } = await supabase.auth.getSession()
          if (retrySession) {
            router.push('/dashboard')
          } else {
            router.push('/login?message=Authentication failed. Please try again.')
          }
        }, 1000)
      }
    }
    
    checkSession()
  }, [router, supabase])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-background">
      <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
      <p className="text-muted-foreground font-medium">Verifying authentication...</p>
    </div>
  )
}
