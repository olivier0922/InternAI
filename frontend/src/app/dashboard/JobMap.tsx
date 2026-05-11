'use client'

import { useEffect, useState, useMemo } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import type { ScoredJob } from './useJobFilters'

// Normal icon
const customIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

// Highlighted icon (red) for hovered jobs
const highlightedIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

export default function JobMap({
  jobs,
  mapCenter,
  mapRadiusKm,
  hoveredJobId,
}: {
  jobs: ScoredJob[]
  mapCenter: [number, number] | null
  mapRadiusKm: number
  hoveredJobId: string | null
}) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  // Only render jobs that have coords
  const jobsWithCoords = useMemo(() => jobs.filter(j => j.latitude != null && j.longitude != null), [jobs])

  if (!mounted) {
    return <div className="h-full w-full rounded-2xl glass animate-pulse" />
  }

  // Calculate dynamic center based on visible jobs if no strict mapCenter is set
  let center: [number, number] = [51.1657, 10.4515] // Germany fallback
  if (mapCenter) {
    center = mapCenter
  } else if (jobsWithCoords.length > 0) {
    // Center on the first visible job to make the map always relevant
    center = [jobsWithCoords[0].latitude!, jobsWithCoords[0].longitude!]
  }

  return (
    <div className="relative h-full w-full overflow-hidden rounded-2xl border border-white/[0.08] shadow-2xl">
      <MapContainer 
        key={`${center[0]}-${center[1]}`} // Force re-render on center change for ease
        center={center} 
        zoom={mapCenter ? 8 : 4} 
        style={{ height: '100%', width: '100%', background: '#0a0a12' }}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Draw search radius circle if an explicit location search was made */}
        {mapCenter && (
          <Circle
            center={mapCenter}
            radius={mapRadiusKm * 1000} // convert km to meters
            pathOptions={{ color: '#8b5cf6', fillColor: '#8b5cf6', fillOpacity: 0.15, weight: 2 }}
          />
        )}

        {/* Render markers for jobs */}
        {jobsWithCoords.map(job => {
          const isHovered = hoveredJobId === job.id
          
          return (
            <Marker 
              key={job.id} 
              position={[job.latitude as number, job.longitude as number]} 
              icon={isHovered ? highlightedIcon : customIcon}
              zIndexOffset={isHovered ? 1000 : 0} // Bring hovered to front
            >
              <Popup className="dark-popup">
                <div className="p-1">
                  <h4 className="font-semibold text-sm mb-1">{job.title}</h4>
                  <p className="text-xs text-gray-500 mb-2">{job.company}</p>
                  <a 
                    href={job.url} 
                    target="_blank" 
                    rel="noreferrer"
                    className="text-xs text-indigo-500 hover:text-indigo-400 font-medium"
                  >
                    View Job &rarr;
                  </a>
                </div>
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>
    </div>
  )
}
