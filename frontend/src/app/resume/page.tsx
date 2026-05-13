'use client'

import { useState, useCallback } from 'react'
import { UploadCloud, FileText, CheckCircle2, File, X } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

// Comprehensive tech skill list for client-side extraction
const KNOWN_SKILLS = [
  // Languages
  'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Ruby', 'PHP', 'Swift',
  'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Haskell', 'Lua', 'Dart', 'Objective-C', 'Shell',
  'Bash', 'PowerShell', 'SQL', 'HTML', 'CSS', 'Sass', 'LESS',
  // Frontend
  'React', 'Angular', 'Vue', 'Vue.js', 'Next.js', 'Nuxt', 'Svelte', 'jQuery', 'Redux', 'Tailwind',
  'Bootstrap', 'Material UI', 'Chakra UI', 'Webpack', 'Vite', 'Storybook',
  // Backend
  'Node.js', 'Express', 'Django', 'Flask', 'FastAPI', 'Spring', 'Spring Boot', '.NET', 'ASP.NET',
  'Rails', 'Ruby on Rails', 'Laravel', 'NestJS', 'GraphQL', 'REST', 'gRPC',
  // Cloud & DevOps
  'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform', 'Ansible',
  'Jenkins', 'CI/CD', 'GitHub Actions', 'GitLab CI', 'CircleCI', 'Helm', 'Prometheus', 'Grafana',
  'Nginx', 'Apache', 'Linux', 'Unix',
  // Databases
  'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'DynamoDB', 'Cassandra',
  'SQLite', 'Oracle', 'SQL Server', 'Firebase', 'Supabase', 'Neo4j', 'InfluxDB',
  // Data & ML
  'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas',
  'NumPy', 'Keras', 'OpenCV', 'NLP', 'Computer Vision', 'Data Science', 'Big Data',
  'Spark', 'Hadoop', 'Airflow', 'dbt', 'Tableau', 'Power BI', 'Jupyter',
  // Mobile
  'React Native', 'Flutter', 'iOS', 'Android', 'SwiftUI', 'Jetpack Compose', 'Xamarin',
  // Tools & Practices
  'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Jira', 'Confluence', 'Agile', 'Scrum',
  'TDD', 'Unit Testing', 'Jest', 'Cypress', 'Selenium', 'Figma', 'Postman',
  // Security
  'Cybersecurity', 'OAuth', 'JWT', 'SSL', 'Encryption', 'Penetration Testing',
  // Other
  'Microservices', 'Serverless', 'WebSocket', 'RabbitMQ', 'Kafka', 'Celery',
  'System Design', 'Design Patterns', 'Data Structures', 'Algorithms', 'OOP',
  'Embedded Systems', 'IoT', 'Blockchain', 'WebAssembly', 'Three.js',
]

function extractSkillsFromText(text: string): string[] {
  const textLower = text.toLowerCase()
  const found: string[] = []

  for (const skill of KNOWN_SKILLS) {
    const skillLower = skill.toLowerCase()
    // For short skills (<=2 chars like C#, R), require word boundary
    if (skillLower.length <= 2) {
      const regex = new RegExp(`\\b${skillLower.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`)
      if (regex.test(textLower)) found.push(skill)
    } else {
      if (textLower.includes(skillLower)) found.push(skill)
    }
  }

  return [...new Set(found)]
}

async function extractTextFromPdf(file: File): Promise<string> {
  const pdfjsLib = await import('pdfjs-dist')
  
  // Use the bundled worker via unpkg which is more reliable
  pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`

  const arrayBuffer = await file.arrayBuffer()
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise

  let fullText = ''
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i)
    const content = await page.getTextContent()
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const pageText = content.items.map((item: any) => item.str).join(' ')
    fullText += pageText + '\n'
  }

  return fullText.trim()
}

export default function ResumePage() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [skills, setSkills] = useState<string[]>([])
  const [success, setSuccess] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const supabase = createClient()
  const router = useRouter()

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files?.[0]) {
      const f = e.dataTransfer.files[0]
      if (f.name.endsWith('.pdf') || f.name.endsWith('.docx')) {
        setFile(f)
        setError('')
      } else {
        setError('Only PDF and DOCX files are supported.')
      }
    }
  }, [])

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError('')
    setSuccess(false)

    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session) {
        router.push('/login')
        return
      }

      // Parse PDF client-side
      let parsedText = ''
      if (file.name.toLowerCase().endsWith('.pdf')) {
        parsedText = await extractTextFromPdf(file)
      } else {
        // For DOCX, we'll read as text (basic fallback)
        parsedText = await file.text()
      }

      if (!parsedText || parsedText.trim().length < 20) {
        throw new Error('Could not extract text from this file. Please try a different PDF.')
      }

      // Extract skills client-side
      const extractedSkills = extractSkillsFromText(parsedText)

      // Upload file to Supabase Storage
      const filePath = `${session.user.id}/${Date.now()}_${file.name}`
      const fileBuffer = await file.arrayBuffer()
      
      await supabase.storage.from('resumes').upload(filePath, fileBuffer, {
        contentType: file.type,
        upsert: false,
      })

      const { data: urlData } = supabase.storage.from('resumes').getPublicUrl(filePath)

      // Store in resumes table
      await supabase.from('resumes').insert({
        user_id: session.user.id,
        file_url: urlData.publicUrl,
        parsed_text: parsedText.slice(0, 10000), // limit size
        extracted_skills: extractedSkills,
      })

      setSkills(extractedSkills)
      setSuccess(true)
      toast.success('Resume uploaded successfully', {
        description: `Extracted ${extractedSkills.length} skills for AI matching.`,
      })

    } catch (err) {
      console.error('Resume upload error:', err)
      setError((err as Error).message || 'An error occurred')
      toast.error('Upload failed', {
        description: (err as Error).message || 'An error occurred during upload.',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-2xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Resume</h1>
          <p className="text-muted-foreground">
            Upload your resume to unlock AI-powered job matching
          </p>
        </div>

        {/* Upload Card */}
        <div className="glass-card rounded-2xl p-8 animate-fade-in">
          <form onSubmit={handleUpload}>
            {/* Error message */}
            {error && (
              <div className="mb-6 p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400 flex items-start gap-2">
                <X className="w-4 h-4 mt-0.5 shrink-0" />
                {error}
              </div>
            )}

            {/* Success message */}
            {success && (
              <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                <div className="flex items-center gap-2 text-emerald-400 font-medium text-sm mb-3">
                  <CheckCircle2 className="w-4 h-4" />
                  Resume uploaded and analyzed successfully!
                </div>
                {skills.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground mb-2">Extracted Skills ({skills.length}):</p>
                    <div className="flex flex-wrap gap-1.5">
                      {skills.map((skill) => (
                        <span
                          key={skill}
                          className="chip chip-active"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Drop zone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`relative border-2 border-dashed rounded-2xl p-6 sm:p-12 text-center transition-all duration-300 ${
                dragActive
                  ? 'border-primary bg-primary/[0.06]'
                  : file
                  ? 'border-emerald-500/30 bg-emerald-500/[0.04]'
                  : 'border-white/10 hover:border-white/20'
              }`}
            >
              {file ? (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                    <File className="w-6 h-6 sm:w-7 sm:h-7 text-emerald-400" />
                  </div>
                  <div>
                    <p className="font-medium text-sm">{file.name}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {(file.size / 1024).toFixed(0)} KB
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => { setFile(null); setSuccess(false); setSkills([]) }}
                    className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                  >
                    Remove file
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center animate-float">
                    <UploadCloud className="w-6 h-6 sm:w-7 sm:h-7 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="font-medium text-sm sm:text-base">
                      Drop your resume here or{' '}
                      <label className="text-primary cursor-pointer hover:text-primary/80 transition-colors">
                        browse
                        <input
                          type="file"
                          accept=".pdf,.docx"
                          onChange={(e) => setFile(e.target.files?.[0] || null)}
                          className="hidden"
                        />
                      </label>
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      PDF or DOCX · Max 10 MB
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Upload button */}
            <button
              type="submit"
              disabled={!file || loading}
              className="w-full gradient-btn text-white font-semibold py-3.5 rounded-xl mt-6 text-sm disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyzing Resume...
                </>
              ) : (
                <>
                  <UploadCloud className="w-4 h-4" />
                  Upload Resume
                </>
              )}
            </button>
          </form>
        </div>

        {/* Info card */}
        <div className="glass-card rounded-2xl p-6 animate-fade-in" style={{ animationDelay: '0.15s' }}>
          <h3 className="font-semibold text-sm mb-3 flex items-center gap-2">
            <FileText className="w-4 h-4 text-primary" />
            How it works
          </h3>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="w-5 h-5 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center shrink-0 mt-0.5 font-medium">1</span>
              Upload your PDF or DOCX resume
            </li>
            <li className="flex items-start gap-2">
              <span className="w-5 h-5 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center shrink-0 mt-0.5 font-medium">2</span>
              Your resume is parsed directly in your browser — nothing leaves your device until you click upload
            </li>
            <li className="flex items-start gap-2">
              <span className="w-5 h-5 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center shrink-0 mt-0.5 font-medium">3</span>
              Extracted skills power the &quot;Strict CV Match&quot; filter on the dashboard
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
