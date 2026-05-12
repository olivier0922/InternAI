import { useMemo, useState, useEffect } from 'react'

export interface Job {
  id: string
  title: string
  company: string
  location: string | null
  remote: boolean
  description: string
  url: string
  source: string
  job_type: string
  tags: string[] | null
  latitude: number | null
  longitude: number | null
  created_at: string
  salary: string | null
}

export interface FilterState {
  searchQuery: string // "What"
  locationQuery: string // "Where"
  remoteOnly: boolean
  mapRadiusKm: number
  mapCenter: [number, number] | null
  datePosted: string    // "all", "24h", "7d", "30d"
  sources: string[]     // Array of source names to include (empty = all)
  sortBy: string        // "relevance" or "date"
}

export const DEFAULT_FILTERS: FilterState = {
  searchQuery: '',
  locationQuery: '',
  remoteOnly: false,
  mapRadiusKm: 50,
  mapCenter: null,
  datePosted: 'all',
  sources: [],
  sortBy: 'relevance',
}

// Haversine distance formula
export function getDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371
  const dLat = (lat2 - lat1) * (Math.PI / 180)
  const dLon = (lon2 - lon1) * (Math.PI / 180)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) *
      Math.cos(lat2 * (Math.PI / 180)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

export type ScoredJob = Job & { relevanceScore: number }

// Simple Levenshtein distance for fuzzy matching
function levenshtein(a: string, b: string): number {
  const m = a.length, n = b.length
  if (m === 0) return n
  if (n === 0) return m
  // Use two-row optimization
  let prev = Array.from({ length: n + 1 }, (_, i) => i)
  let curr = new Array(n + 1)
  for (let i = 1; i <= m; i++) {
    curr[0] = i
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1
      curr[j] = Math.min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
    }
    ;[prev, curr] = [curr, prev]
  }
  return prev[n]
}

// Check if term fuzzy-matches any word in text (within distance 1-2)
function fuzzyMatch(term: string, words: string[]): boolean {
  if (term.length < 4) return false // Only fuzzy match longer terms
  const maxDist = term.length <= 5 ? 1 : 2
  return words.some(w => {
    if (Math.abs(w.length - term.length) > maxDist) return false
    return levenshtein(term, w) <= maxDist
  })
}

export function useJobFilters(jobs: Job[], filters: FilterState, userSkills: string[] = []) {
  return useMemo(() => {
    let results: ScoredJob[] = jobs.map(j => ({ ...j, relevanceScore: 0 }))

    // 1. Remote Only Filter
    if (filters.remoteOnly) {
      results = results.filter(job => job.remote)
    }

    // 1.5. Location Text Filter
    if (filters.locationQuery.trim() !== '') {
      const locQ = filters.locationQuery.toLowerCase().trim()
      results = results.filter(job => 
        (job.location && job.location.toLowerCase().includes(locQ)) || 
        // If a user types a location but the job is purely "Remote" without a location string, it's a design choice whether to include it.
        // Let's include jobs where location string contains the query. If they want remote, they can click remote.
        (job.remote && locQ === 'remote')
      )
    }

    // 3. Date Posted Filter
    if (filters.datePosted && filters.datePosted !== 'all') {
      const now = Date.now()
      const cutoffs: Record<string, number> = {
        '24h': 24 * 60 * 60 * 1000,
        '7d': 7 * 24 * 60 * 60 * 1000,
        '30d': 30 * 24 * 60 * 60 * 1000,
      }
      const cutoff = cutoffs[filters.datePosted]
      if (cutoff) {
        results = results.filter(job => now - new Date(job.created_at).getTime() <= cutoff)
      }
    }

    // 4. Source Filter
    if (filters.sources.length > 0) {
      results = results.filter(job => filters.sources.includes(job.source))
    }

    // 5. Geographic Radius Filter
    if (filters.mapCenter && filters.mapRadiusKm !== null) {
      results = results.filter(job => {
        if (job.latitude == null || job.longitude == null) return false
        const dist = getDistance(filters.mapCenter![0], filters.mapCenter![1], job.latitude, job.longitude)
        return dist <= filters.mapRadiusKm
      })
    }

    // 7. Intelligent Scoring Engine ("What" search + Resume Skills)
    const query = filters.searchQuery.toLowerCase().trim()
    const hasSearchQuery = query !== ''
    const hasSkills = userSkills && userSkills.length > 0

    if (hasSearchQuery || hasSkills) {
      const terms = hasSearchQuery ? query.split(/\s+/).filter(t => t.length > 0) : []
      const skillTerms = hasSkills ? userSkills.map(s => s.toLowerCase().trim()) : []
      
      results.forEach(job => {
        let textScore = 0
        const titleLower = job.title.toLowerCase()
        const companyLower = job.company.toLowerCase()
        const descLower = job.description.toLowerCase()
        const locationLower = (job.location || '').toLowerCase()
        const tagsLower = (job.tags || []).map(t => t.toLowerCase())
        const titleWords = titleLower.split(/\s+/)
        const companyWords = companyLower.split(/\s+/)

        // Search Query Scoring
        if (hasSearchQuery) {
          // Exact full-query match in title = massive boost
          if (titleLower.includes(query)) textScore += 50
          // Exact full-query match in company
          if (companyLower.includes(query)) textScore += 30

          terms.forEach(term => {
            // Title exact word match
            if (titleWords.includes(term)) textScore += 15
            // Title substring match
            else if (titleLower.includes(term)) textScore += 10
            // Title fuzzy match
            else if (fuzzyMatch(term, titleWords)) textScore += 5
            
            // Company exact match
            if (companyWords.includes(term)) textScore += 8
            else if (companyLower.includes(term)) textScore += 5
            
            // Tag match
            if (tagsLower.some(t => t.includes(term))) textScore += 4
            
            // Location match
            if (locationLower.includes(term)) textScore += 3
            
            // Description match
            if (descLower.includes(term)) textScore += 2
          })
        }

        // Resume Skills Scoring
        if (hasSkills) {
          let matchedSkills = 0
          skillTerms.forEach(skill => {
            if (titleLower.includes(skill)) {
              textScore += 20 // Huge boost if skill is in title
              matchedSkills++
            } else if (tagsLower.some(t => t === skill || t.includes(skill))) {
              textScore += 10 // Big boost for explicit tags
              matchedSkills++
            } else if (descLower.includes(skill)) {
              textScore += 5  // Moderate boost if mentioned in description
              matchedSkills++
            }
          })
          
          // Synergy bonus: if multiple resume skills match, exponentially boost
          if (matchedSkills >= 2) {
            textScore += (matchedSkills * 5)
          }
        }
        
        // Only add bonuses if there's at least some text or skill match, or if neither was provided
        let score = textScore
        if (textScore > 0 || (!hasSearchQuery && !hasSkills)) {
          // Date decay: newer jobs get a slight boost (up to 5 points)
          const ageMs = Date.now() - new Date(job.created_at).getTime()
          const ageDays = ageMs / (1000 * 60 * 60 * 24)
          score += Math.max(0, 5 - ageDays * 0.2)
          // Salary bonus
          if (job.salary) score += 1
        }
        
        job.relevanceScore = score
      })

      // Drop jobs with no match if searching (but if only skills, maybe keep them just sorted lower?)
      if (hasSearchQuery) {
        results = results.filter(job => job.relevanceScore >= 2)
      }
      
      // Sort by score descending, then by newest
      results.sort((a, b) => {
        if (Math.abs(b.relevanceScore - a.relevanceScore) > 0.5) {
          return b.relevanceScore - a.relevanceScore
        }
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      })
    } else {
      // No search query and no skills: sort by newest
      if (filters.sortBy === 'date' || !filters.searchQuery) {
        results.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      }
    }

    return results
  }, [jobs, filters, userSkills])
}

// Client-side geocoding hook for "Where" input
export function useGeocode(locationQuery: string) {
  const [coords, setCoords] = useState<[number, number] | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!locationQuery || locationQuery.trim().length < 3) {
      setCoords(null)
      return
    }

    const timeout = setTimeout(async () => {
      setLoading(true)
      try {
        const res = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(locationQuery)}&format=json&limit=1`)
        if (res.ok) {
          const data = await res.json()
          if (data && data.length > 0) {
            setCoords([parseFloat(data[0].lat), parseFloat(data[0].lon)])
          } else {
            setCoords(null)
          }
        }
      } catch (err) {
        console.error("Geocoding failed", err)
      } finally {
        setLoading(false)
      }
    }, 600) // Debounce

    return () => clearTimeout(timeout)
  }, [locationQuery])

  return { coords, loading }
}
