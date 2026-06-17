import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import {
  AnimatePresence,
  motion,
  useReducedMotion,
  type Variants,
} from 'framer-motion'

/* -------------------------------------------------------------------------- */
/*  Types & constants                                                          */
/* -------------------------------------------------------------------------- */

type AspectKey = '9:16' | '1:1' | '16:9' | 'original'
type FilterKey = 'clean' | 'cinematic' | 'vibrant' | 'noir' | 'warm'
type CaptionStyle = 'glass' | 'bold' | 'minimal'
type CaptionPosition = 'top' | 'center' | 'bottom'

interface AspectOption {
  key: AspectKey
  label: string
  ratio: string
  note: string
}

const ASPECTS: AspectOption[] = [
  { key: '9:16', label: '9 : 16', ratio: 'Vertical', note: 'TikTok · Reels · Shorts' },
  { key: '1:1', label: '1 : 1', ratio: 'Square', note: 'Feed posts' },
  { key: '16:9', label: '16 : 9', ratio: 'Wide', note: 'YouTube · X · LinkedIn' },
  { key: 'original', label: 'Auto', ratio: 'Original', note: 'Keep source frame' },
]

const FILTERS: { key: FilterKey; label: string; css: string }[] = [
  { key: 'clean', label: 'Clean', css: 'saturate(1.03) contrast(1.02)' },
  {
    key: 'cinematic',
    label: 'Cinematic',
    css: 'contrast(1.16) saturate(0.92) brightness(0.96) sepia(0.12)',
  },
  { key: 'vibrant', label: 'Vibrant', css: 'saturate(1.5) contrast(1.08) brightness(1.03)' },
  { key: 'noir', label: 'Noir', css: 'grayscale(1) contrast(1.25) brightness(1.02)' },
  { key: 'warm', label: 'Warm', css: 'sepia(0.28) saturate(1.25) brightness(1.04)' },
]

const CAPTION_STYLES: { key: CaptionStyle; label: string }[] = [
  { key: 'glass', label: 'Glass' },
  { key: 'bold', label: 'Bold' },
  { key: 'minimal', label: 'Minimal' },
]

const CAPTION_POSITIONS: { key: CaptionPosition; label: string }[] = [
  { key: 'top', label: 'Top' },
  { key: 'center', label: 'Center' },
  { key: 'bottom', label: 'Bottom' },
]

const CAPTION_IDEAS = [
  'Wait for it…',
  'POV: you finally get it',
  'The part nobody talks about',
  'Save this for later',
  'Watch till the end 👀',
  'This changed everything',
]

const FAQS: { q: string; a: string }[] = [
  {
    q: 'Does my video get uploaded to a server?',
    a: 'No. ClipForge Studio runs entirely in your browser. Your file is loaded locally as an object URL and never leaves your device — there is no backend.',
  },
  {
    q: 'Why is the export a WebM file and not MP4?',
    a: 'Browsers can record canvas output to WebM natively via the MediaRecorder API. True MP4 (H.264) encoding is not exposed to the browser, so it requires either server-side encoding or a heavier WebAssembly encoder like ffmpeg.wasm. WebM plays on all major platforms and uploads cleanly to TikTok, Reels, Shorts, YouTube and X.',
  },
  {
    q: 'Will my clip include sound?',
    a: 'Yes, when your browser supports capturing audio tracks from the video element. If audio capture is unavailable, the clip is still rendered as a clean, silent video and we let you know.',
  },
  {
    q: 'What video formats can I upload?',
    a: 'Any file your browser can play — typically MP4 (H.264), WebM and many MOV files. If a file fails to load, try converting it to MP4 first.',
  },
  {
    q: 'Why does export run in real time?',
    a: 'Browser recording captures the canvas as it plays, so a 15-second clip takes about 15 seconds to render. Keep the tab focused while rendering for the smoothest result.',
  },
]

/* -------------------------------------------------------------------------- */
/*  Helpers                                                                    */
/* -------------------------------------------------------------------------- */

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) seconds = 0
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  const t = Math.floor((seconds * 10) % 10)
  return `${m}:${String(s).padStart(2, '0')}.${t}`
}

function clamp(v: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, v))
}

/** Target canvas dimensions for a given aspect + source video size. */
function targetDimensions(
  aspect: AspectKey,
  vw: number,
  vh: number,
): { w: number; h: number } {
  switch (aspect) {
    case '9:16':
      return { w: 540, h: 960 }
    case '1:1':
      return { w: 720, h: 720 }
    case '16:9':
      return { w: 960, h: 540 }
    case 'original':
    default: {
      if (!vw || !vh) return { w: 960, h: 540 }
      const cap = 960
      const scale = Math.min(1, cap / Math.max(vw, vh))
      return { w: Math.round(vw * scale), h: Math.round(vh * scale) }
    }
  }
}

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
) {
  const radius = Math.min(r, w / 2, h / 2)
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.arcTo(x + w, y, x + w, y + h, radius)
  ctx.arcTo(x + w, y + h, x, y + h, radius)
  ctx.arcTo(x, y + h, x, y, radius)
  ctx.arcTo(x, y, x + w, y, radius)
  ctx.closePath()
}

function wrapText(
  ctx: CanvasRenderingContext2D,
  text: string,
  maxWidth: number,
): string[] {
  const words = text.split(/\s+/).filter(Boolean)
  const lines: string[] = []
  let current = ''
  for (const word of words) {
    const test = current ? `${current} ${word}` : word
    if (ctx.measureText(test).width > maxWidth && current) {
      lines.push(current)
      current = word
    } else {
      current = test
    }
  }
  if (current) lines.push(current)
  return lines.slice(0, 4)
}

function pickMimeType(): string | null {
  if (typeof MediaRecorder === 'undefined') return null
  const candidates = [
    'video/webm;codecs=vp9,opus',
    'video/webm;codecs=vp8,opus',
    'video/webm;codecs=vp9',
    'video/webm;codecs=vp8',
    'video/webm',
  ]
  for (const type of candidates) {
    try {
      if (MediaRecorder.isTypeSupported(type)) return type
    } catch {
      /* ignore */
    }
  }
  return null
}

/* -------------------------------------------------------------------------- */
/*  Animation variants                                                         */
/* -------------------------------------------------------------------------- */

const containerVariants: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08, delayChildren: 0.05 } },
}

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } },
}

/* -------------------------------------------------------------------------- */
/*  Small UI primitives                                                        */
/* -------------------------------------------------------------------------- */

function Reveal({
  children,
  className,
  delay = 0,
}: {
  children: ReactNode
  className?: string
  delay?: number
}) {
  const reduce = useReducedMotion()
  return (
    <motion.div
      className={className}
      initial={reduce ? false : { opacity: 0, y: 30 }}
      whileInView={reduce ? undefined : { opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay }}
    >
      {children}
    </motion.div>
  )
}

function SectionHeading({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string
  title: ReactNode
  subtitle?: string
}) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      <span className="inline-block rounded-full border border-white/10 bg-white/5 px-4 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-brand-soft">
        {eyebrow}
      </span>
      <h2 className="mt-5 text-3xl font-extrabold tracking-tight text-white sm:text-4xl md:text-5xl">
        {title}
      </h2>
      {subtitle && (
        <p className="mt-4 text-base leading-relaxed text-slate-400 sm:text-lg">
          {subtitle}
        </p>
      )}
    </div>
  )
}

function Pill({
  active,
  onClick,
  children,
  ariaLabel,
}: {
  active: boolean
  onClick: () => void
  children: ReactNode
  ariaLabel?: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      aria-label={ariaLabel}
      className={[
        'rounded-xl px-3 py-2 text-sm font-semibold transition-all duration-200',
        'border focus-visible:outline-none',
        active
          ? 'border-transparent bg-brand-gradient text-white shadow-glow'
          : 'border-white/10 bg-white/[0.03] text-slate-300 hover:border-white/20 hover:bg-white/[0.07]',
      ].join(' ')}
    >
      {children}
    </button>
  )
}

/* -------------------------------------------------------------------------- */
/*  Main App                                                                   */
/* -------------------------------------------------------------------------- */

export default function App() {
  const reduce = useReducedMotion()

  // Media + meta
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string>('')
  const [duration, setDuration] = useState(0)
  const [naturalSize, setNaturalSize] = useState({ w: 0, h: 0 })
  const [currentTime, setCurrentTime] = useState(0)
  const [uploadError, setUploadError] = useState<string | null>(null)

  // Edit settings
  const [start, setStart] = useState(0)
  const [end, setEnd] = useState(0)
  const [aspect, setAspect] = useState<AspectKey>('9:16')
  const [filter, setFilter] = useState<FilterKey>('clean')
  const [caption, setCaption] = useState('')
  const [captionStyle, setCaptionStyle] = useState<CaptionStyle>('glass')
  const [captionPosition, setCaptionPosition] = useState<CaptionPosition>('bottom')
  const [captionSize, setCaptionSize] = useState(5)

  // Export
  const [isExporting, setIsExporting] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)
  const [exportUrl, setExportUrl] = useState<string | null>(null)
  const [exportError, setExportError] = useState<string | null>(null)
  const [exportHadAudio, setExportHadAudio] = useState(false)

  // Refs
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const rafRef = useRef<number>(0)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const previewingRef = useRef(false)
  const exportingRef = useRef(false)

  // Mutable mirror of settings for the animation loop (avoids stale closures)
  const settingsRef = useRef({
    start: 0,
    end: 0,
    aspect: '9:16' as AspectKey,
    filter: 'clean' as FilterKey,
    caption: '',
    captionStyle: 'glass' as CaptionStyle,
    captionPosition: 'bottom' as CaptionPosition,
    captionSize: 5,
  })
  settingsRef.current = {
    start,
    end,
    aspect,
    filter,
    caption,
    captionStyle,
    captionPosition,
    captionSize,
  }

  const clipLength = Math.max(0, end - start)
  const exportSupported = useMemo(() => pickMimeType() !== null, [])

  /* ------------------------------ Upload ------------------------------ */

  const handleFile = useCallback(
    (file: File | undefined | null) => {
      setUploadError(null)
      setExportUrl(null)
      setExportError(null)
      if (!file) return
      if (!file.type.startsWith('video/')) {
        setUploadError('That file is not a video. Please choose an MP4, WebM or MOV file.')
        return
      }
      try {
        const url = URL.createObjectURL(file)
        // Revoke any previous object URL.
        setVideoUrl((prev) => {
          if (prev) URL.revokeObjectURL(prev)
          return url
        })
        setFileName(file.name)
      } catch {
        setUploadError('We could not read that file. Please try a different video.')
      }
    },
    [],
  )

  const onMetadata = useCallback(() => {
    const v = videoRef.current
    if (!v) return
    const d = Number.isFinite(v.duration) ? v.duration : 0
    setDuration(d)
    setNaturalSize({ w: v.videoWidth, h: v.videoHeight })
    const initialEnd = Math.min(d, 30)
    setStart(0)
    setEnd(initialEnd > 0 ? initialEnd : d)
    setCurrentTime(0)
  }, [])

  /* --------------------------- Smart starters --------------------------- */

  const smartStarters = useMemo(() => {
    if (!duration) return []
    const d = duration
    const mid = d / 2
    return [
      { label: 'Opening hook', desc: 'First 15 seconds', s: 0, e: Math.min(d, 15) },
      {
        label: 'Mid-video highlight',
        desc: 'Around the midpoint',
        s: Math.max(0, mid - 7),
        e: Math.min(d, mid + 8),
      },
      {
        label: 'Closing punch',
        desc: 'The final beat',
        s: Math.max(0, d - 15),
        e: d,
      },
    ]
  }, [duration])

  const applyRange = useCallback((s: number, e: number) => {
    setStart(s)
    setEnd(e)
    const v = videoRef.current
    if (v) {
      v.currentTime = s
      setCurrentTime(s)
    }
  }, [])

  /* --------------------------- Trim controls --------------------------- */

  const setStartHere = useCallback(() => {
    const v = videoRef.current
    if (!v) return
    const t = clamp(v.currentTime, 0, Math.max(0, end - 0.5))
    setStart(t)
  }, [end])

  const setEndHere = useCallback(() => {
    const v = videoRef.current
    if (!v) return
    const t = clamp(v.currentTime, start + 0.5, duration)
    setEnd(t)
  }, [start, duration])

  const onStartSlider = (value: number) => setStart(clamp(value, 0, Math.max(0, end - 0.5)))
  const onEndSlider = (value: number) =>
    setEnd(clamp(value, Math.min(duration, start + 0.5), duration))

  /* --------------------------- Clip preview --------------------------- */

  const previewClip = useCallback(() => {
    const v = videoRef.current
    if (!v) return
    v.currentTime = settingsRef.current.start
    previewingRef.current = true
    v.play().catch(() => {
      previewingRef.current = false
      setUploadError('Playback was blocked. Tap the video controls to start it manually.')
    })
  }, [])

  /* --------------------------- Canvas drawing --------------------------- */

  const drawCaption = useCallback(
    (ctx: CanvasRenderingContext2D, w: number, h: number) => {
      const s = settingsRef.current
      const text = s.caption.trim()
      if (!text) return

      const fontSize = Math.round(h * (0.04 + s.captionSize * 0.012))
      const isBold = s.captionStyle === 'bold'
      ctx.font = `${isBold ? 900 : 800} ${fontSize}px Inter, system-ui, sans-serif`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      const display = isBold ? text.toUpperCase() : text
      const maxWidth = w * 0.86
      const lines = wrapText(ctx, display, maxWidth)
      const lineHeight = fontSize * 1.22
      const blockH = lines.length * lineHeight
      const margin = h * 0.07

      let centerY: number
      if (s.captionPosition === 'top') centerY = margin + blockH / 2
      else if (s.captionPosition === 'center') centerY = h / 2
      else centerY = h - margin - blockH / 2

      const widest = Math.max(...lines.map((l) => ctx.measureText(l).width), 0)
      const padX = fontSize * 0.55
      const padY = fontSize * 0.4
      const bgW = Math.min(w * 0.94, widest + padX * 2)
      const bgH = blockH + padY * 2
      const bgX = (w - bgW) / 2
      const bgY = centerY - bgH / 2

      if (s.captionStyle === 'glass') {
        ctx.save()
        ctx.fillStyle = 'rgba(8, 10, 20, 0.46)'
        roundRect(ctx, bgX, bgY, bgW, bgH, fontSize * 0.45)
        ctx.fill()
        ctx.lineWidth = Math.max(1, fontSize * 0.03)
        ctx.strokeStyle = 'rgba(255,255,255,0.18)'
        ctx.stroke()
        ctx.restore()
      } else if (s.captionStyle === 'bold') {
        ctx.save()
        ctx.fillStyle = 'rgba(6, 7, 13, 0.86)'
        roundRect(ctx, bgX, bgY, bgW, bgH, fontSize * 0.18)
        ctx.fill()
        ctx.restore()
      }

      // Text
      ctx.save()
      const top = centerY - blockH / 2 + lineHeight / 2
      if (s.captionStyle === 'minimal') {
        ctx.shadowColor = 'rgba(0,0,0,0.65)'
        ctx.shadowBlur = fontSize * 0.35
        ctx.shadowOffsetY = fontSize * 0.04
      }
      lines.forEach((line, i) => {
        if (s.captionStyle === 'bold') {
          ctx.fillStyle = '#a78bfa'
          ctx.fillText(line, w / 2, top + i * lineHeight + fontSize * 0.04)
        }
        ctx.fillStyle = '#ffffff'
        ctx.fillText(line, w / 2, top + i * lineHeight)
      })
      ctx.restore()
    },
    [],
  )

  const drawFrame = useCallback(() => {
    const v = videoRef.current
    const canvas = canvasRef.current
    if (!v || !canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const s = settingsRef.current
    const { w, h } = targetDimensions(s.aspect, v.videoWidth, v.videoHeight)
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w
      canvas.height = h
    }

    // Background
    ctx.clearRect(0, 0, w, h)
    ctx.fillStyle = '#06070d'
    ctx.fillRect(0, 0, w, h)

    if (v.readyState >= 2 && v.videoWidth && v.videoHeight) {
      const vw = v.videoWidth
      const vh = v.videoHeight
      const targetRatio = w / h
      const videoRatio = vw / vh
      let sx = 0
      let sy = 0
      let sw = vw
      let sh = vh
      if (videoRatio > targetRatio) {
        // video wider than frame -> crop sides
        sw = vh * targetRatio
        sx = (vw - sw) / 2
      } else {
        // video taller -> crop top/bottom
        sh = vw / targetRatio
        sy = (vh - sh) / 2
      }
      const css = FILTERS.find((f) => f.key === s.filter)?.css ?? 'none'
      ctx.save()
      ctx.filter = css
      try {
        ctx.drawImage(v, sx, sy, sw, sh, 0, 0, w, h)
      } catch {
        /* frame not paintable yet */
      }
      ctx.restore()
      ctx.filter = 'none'
    }

    // Captions
    drawCaption(ctx, w, h)

    // Progress overlay (export or in-range playback)
    const range = Math.max(0.001, s.end - s.start)
    const within = clamp((v.currentTime - s.start) / range, 0, 1)
    const showBar = exportingRef.current || previewingRef.current
    if (showBar) {
      const barH = Math.max(4, h * 0.012)
      const pad = w * 0.04
      const barW = w - pad * 2
      const by = h - barH - h * 0.025
      ctx.save()
      ctx.fillStyle = 'rgba(255,255,255,0.18)'
      roundRect(ctx, pad, by, barW, barH, barH / 2)
      ctx.fill()
      const grad = ctx.createLinearGradient(pad, 0, pad + barW, 0)
      grad.addColorStop(0, '#a78bfa')
      grad.addColorStop(1, '#22d3ee')
      ctx.fillStyle = grad
      roundRect(ctx, pad, by, Math.max(barH, barW * within), barH, barH / 2)
      ctx.fill()
      ctx.restore()
    }
  }, [drawCaption])

  // Single render loop, runs while a video is loaded.
  useEffect(() => {
    if (!videoUrl) return
    let active = true
    const loop = () => {
      if (!active) return
      const v = videoRef.current
      drawFrame()
      if (v) {
        const s = settingsRef.current
        if (previewingRef.current && v.currentTime >= s.end) {
          previewingRef.current = false
          v.pause()
        }
        if (exportingRef.current) {
          const range = Math.max(0.001, s.end - s.start)
          setExportProgress(clamp((v.currentTime - s.start) / range, 0, 1))
          if (v.currentTime >= s.end || v.ended) {
            finishExport()
          }
        }
      }
      rafRef.current = requestAnimationFrame(loop)
    }
    rafRef.current = requestAnimationFrame(loop)
    return () => {
      active = false
      cancelAnimationFrame(rafRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [videoUrl, drawFrame])

  /* ------------------------------ Export ------------------------------ */

  const finishExport = useCallback(() => {
    if (!exportingRef.current) return
    exportingRef.current = false
    const v = videoRef.current
    if (v) v.pause()
    const recorder = recorderRef.current
    if (recorder && recorder.state !== 'inactive') {
      recorder.stop()
    }
  }, [])

  const startExport = useCallback(() => {
    const v = videoRef.current
    const canvas = canvasRef.current
    setExportError(null)
    setExportUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev)
      return null
    })

    if (!v || !canvas) {
      setExportError('Upload a video before rendering.')
      return
    }
    if (clipLength < 0.4) {
      setExportError('Your clip is too short. Choose a range of at least half a second.')
      return
    }
    const mimeType = pickMimeType()
    if (!mimeType) {
      setExportError(
        'Your browser does not support in-browser video recording. Try the latest Chrome, Edge or Firefox.',
      )
      return
    }

    let stream: MediaStream
    try {
      stream = canvas.captureStream(30)
    } catch {
      setExportError('Could not capture the canvas in this browser. Please update your browser.')
      return
    }

    // Try to attach audio from the source video.
    let hadAudio = false
    try {
      const anyVideo = v as HTMLVideoElement & {
        captureStream?: () => MediaStream
        mozCaptureStream?: () => MediaStream
      }
      const vStream =
        anyVideo.captureStream?.() ?? anyVideo.mozCaptureStream?.() ?? null
      const audioTracks = vStream?.getAudioTracks() ?? []
      if (audioTracks.length) {
        audioTracks.forEach((track) => stream.addTrack(track))
        hadAudio = true
      }
    } catch {
      hadAudio = false
    }
    setExportHadAudio(hadAudio)

    let recorder: MediaRecorder
    try {
      recorder = new MediaRecorder(stream, { mimeType })
    } catch {
      setExportError('Recording failed to start. Please try again.')
      return
    }
    chunksRef.current = []
    recorderRef.current = recorder
    recorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) chunksRef.current.push(e.data)
    }
    recorder.onstop = () => {
      try {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' })
        const url = URL.createObjectURL(blob)
        setExportUrl(url)
      } catch {
        setExportError('We could not assemble the rendered clip. Please try again.')
      }
      setIsExporting(false)
      setExportProgress(1)
    }
    recorder.onerror = () => {
      setExportError('Something went wrong while rendering. Please try again.')
      exportingRef.current = false
      setIsExporting(false)
    }

    setIsExporting(true)
    setExportProgress(0)
    exportingRef.current = true
    previewingRef.current = false

    // Seek to the in-point, then play and start recording.
    v.currentTime = settingsRef.current.start
    v.play()
      .then(() => {
        try {
          recorder.start(100)
        } catch {
          setExportError('Recording failed to start. Please try again.')
          exportingRef.current = false
          setIsExporting(false)
        }
      })
      .catch(() => {
        setExportError(
          'Playback was blocked, so the clip could not be recorded. Interact with the page and try again.',
        )
        exportingRef.current = false
        setIsExporting(false)
      })
  }, [clipLength])

  const cancelExport = useCallback(() => {
    exportingRef.current = false
    const recorder = recorderRef.current
    if (recorder && recorder.state !== 'inactive') recorder.stop()
    const v = videoRef.current
    if (v) v.pause()
    setIsExporting(false)
  }, [])

  /* --------------------------- Cleanup on unmount --------------------------- */

  useEffect(() => {
    return () => {
      if (videoUrl) URL.revokeObjectURL(videoUrl)
      if (exportUrl) URL.revokeObjectURL(exportUrl)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const downloadName = useMemo(() => {
    const base = fileName.replace(/\.[^.]+$/, '') || 'clip'
    return `${base}-clipforge.webm`
  }, [fileName])

  const activeFilterCss = FILTERS.find((f) => f.key === filter)?.css ?? 'none'

  /* ----------------------------------------------------------------------- */
  /*  Render                                                                 */
  /* ----------------------------------------------------------------------- */

  return (
    <div className="min-h-screen bg-ink-950 text-slate-100 selection:bg-brand/40">
      {/* Ambient background */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-10 bg-radial-fade"
      />
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-10 opacity-[0.04]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.6) 1px, transparent 1px)',
          backgroundSize: '64px 64px',
        }}
      />

      <Navbar />

      <main>
        <Hero
          reduce={!!reduce}
          hasVideo={!!videoUrl}
          onPickFile={handleFile}
        />

        {/* -------------------------- STUDIO -------------------------- */}
        <section
          id="studio"
          className="mx-auto w-full max-w-7xl scroll-mt-24 px-4 py-16 sm:px-6 sm:py-24 lg:px-8"
          aria-label="Video editor studio"
        >
          <Reveal>
            <SectionHeading
              eyebrow="The Studio"
              title={
                <>
                  Forge your <span className="text-gradient">scroll-stopping</span> clip
                </>
              }
              subtitle="Upload, trim, crop, caption and render — everything happens locally in your browser."
            />
          </Reveal>

          <div className="mt-12 grid grid-cols-1 gap-6 lg:grid-cols-12">
            {/* LEFT: source + canvas */}
            <div className="space-y-6 lg:col-span-7">
              {/* Upload / Source monitor */}
              <Reveal>
                <div className="glass rounded-3xl p-4 shadow-premium sm:p-6">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <h3 className="text-sm font-semibold uppercase tracking-widest text-slate-400">
                      Source monitor
                    </h3>
                    {fileName && (
                      <span className="max-w-[55%] truncate rounded-full bg-white/5 px-3 py-1 text-xs text-slate-300">
                        {fileName}
                      </span>
                    )}
                  </div>

                  {!videoUrl ? (
                    <UploadDropzone onPickFile={handleFile} />
                  ) : (
                    <div className="overflow-hidden rounded-2xl border border-white/10 bg-black">
                      <video
                        ref={videoRef}
                        src={videoUrl}
                        controls
                        playsInline
                        crossOrigin="anonymous"
                        className="aspect-video w-full bg-black"
                        onLoadedMetadata={onMetadata}
                        onTimeUpdate={(e) =>
                          setCurrentTime((e.target as HTMLVideoElement).currentTime)
                        }
                        onError={() =>
                          setUploadError(
                            'This video could not be played. Try a standard MP4 (H.264) or WebM file.',
                          )
                        }
                      >
                        Your browser does not support the video element.
                      </video>
                    </div>
                  )}

                  {uploadError && (
                    <p
                      role="alert"
                      className="mt-3 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-200"
                    >
                      {uploadError}
                    </p>
                  )}

                  {videoUrl && (
                    <div className="mt-4 flex flex-wrap items-center gap-3">
                      <label className="cursor-pointer rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-white/20 hover:bg-white/[0.07]">
                        Replace video
                        <input
                          type="file"
                          accept="video/*"
                          className="sr-only"
                          onChange={(e) => handleFile(e.target.files?.[0])}
                        />
                      </label>
                      <span className="text-xs text-slate-500">
                        {naturalSize.w}×{naturalSize.h} · {formatTime(duration)} total
                      </span>
                    </div>
                  )}
                </div>
              </Reveal>

              {/* Canvas output preview */}
              <Reveal delay={0.05}>
                <div className="glass rounded-3xl p-4 shadow-premium sm:p-6">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <h3 className="text-sm font-semibold uppercase tracking-widest text-slate-400">
                      Output preview
                    </h3>
                    <span className="rounded-full bg-brand/15 px-3 py-1 text-xs font-medium text-brand-soft">
                      {ASPECTS.find((a) => a.key === aspect)?.label} · {filter}
                    </span>
                  </div>

                  <div className="flex justify-center">
                    <div
                      className="relative w-full overflow-hidden rounded-2xl border border-white/10 bg-black"
                      style={{
                        maxWidth:
                          aspect === '9:16' ? 360 : aspect === '1:1' ? 480 : '100%',
                      }}
                    >
                      <canvas
                        ref={canvasRef}
                        className="block h-auto w-full"
                        aria-label="Edited clip preview"
                        role="img"
                      />
                      {!videoUrl && (
                        <div className="flex aspect-[9/16] w-full items-center justify-center p-8 text-center sm:aspect-video">
                          <p className="text-sm text-slate-500">
                            Your edited frame will render here once you upload a video.
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="mt-5 flex flex-col gap-3 sm:flex-row">
                    <button
                      type="button"
                      onClick={previewClip}
                      disabled={!videoUrl}
                      className="flex-1 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-semibold text-white transition hover:border-white/25 hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      ▶ Preview selected clip
                    </button>
                    {!isExporting ? (
                      <button
                        type="button"
                        onClick={startExport}
                        disabled={!videoUrl || !exportSupported}
                        className="flex-1 rounded-xl bg-brand-gradient px-4 py-3 text-sm font-bold text-white shadow-glow transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        ⚡ Render clip
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={cancelExport}
                        className="flex-1 rounded-xl border border-red-400/30 bg-red-500/15 px-4 py-3 text-sm font-bold text-red-100 transition hover:bg-red-500/25"
                      >
                        ■ Stop rendering ({Math.round(exportProgress * 100)}%)
                      </button>
                    )}
                  </div>

                  {/* Export status */}
                  <AnimatePresence>
                    {isExporting && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-4 overflow-hidden"
                      >
                        <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
                          <div
                            className="h-full rounded-full bg-brand-gradient transition-[width] duration-150"
                            style={{ width: `${Math.round(exportProgress * 100)}%` }}
                          />
                        </div>
                        <p className="mt-2 text-xs text-slate-400">
                          Rendering in real time — keep this tab focused…
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {exportError && (
                    <p
                      role="alert"
                      className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-200"
                    >
                      {exportError}
                    </p>
                  )}

                  {exportUrl && !isExporting && (
                    <motion.div
                      initial={reduce ? false : { opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-4 rounded-2xl border border-emerald-400/20 bg-emerald-400/[0.06] p-4"
                    >
                      <p className="text-sm font-semibold text-emerald-200">
                        ✓ Your clip is ready{exportHadAudio ? ' (with audio)' : ' (no audio track captured)'}.
                      </p>
                      <video
                        src={exportUrl}
                        controls
                        playsInline
                        className="mt-3 w-full rounded-xl border border-white/10 bg-black"
                      />
                      <div className="mt-3 flex flex-wrap items-center gap-3">
                        <a
                          href={exportUrl}
                          download={downloadName}
                          className="rounded-xl bg-brand-gradient px-5 py-2.5 text-sm font-bold text-white shadow-glow transition hover:brightness-110"
                        >
                          ↓ Download WebM
                        </a>
                        <span className="text-xs text-slate-400">
                          MP4 (H.264) needs server-side or WebAssembly encoding — WebM uploads everywhere.
                        </span>
                      </div>
                    </motion.div>
                  )}
                </div>
              </Reveal>
            </div>

            {/* RIGHT: controls */}
            <div className="space-y-6 lg:col-span-5">
              {/* Trim */}
              <Reveal>
                <ControlCard title="Trim" badge={`${formatTime(clipLength)} clip`}>
                  <div className="space-y-5">
                    <div>
                      <div className="mb-1.5 flex items-center justify-between">
                        <label htmlFor="start-range" className="text-sm font-medium text-slate-300">
                          Start
                        </label>
                        <span className="font-mono text-sm text-brand-soft">
                          {formatTime(start)}
                        </span>
                      </div>
                      <input
                        id="start-range"
                        type="range"
                        min={0}
                        max={duration || 0}
                        step={0.1}
                        value={start}
                        disabled={!videoUrl}
                        onChange={(e) => onStartSlider(Number(e.target.value))}
                        aria-label="Clip start time"
                      />
                    </div>
                    <div>
                      <div className="mb-1.5 flex items-center justify-between">
                        <label htmlFor="end-range" className="text-sm font-medium text-slate-300">
                          End
                        </label>
                        <span className="font-mono text-sm text-brand-soft">
                          {formatTime(end)}
                        </span>
                      </div>
                      <input
                        id="end-range"
                        type="range"
                        min={0}
                        max={duration || 0}
                        step={0.1}
                        value={end}
                        disabled={!videoUrl}
                        onChange={(e) => onEndSlider(Number(e.target.value))}
                        aria-label="Clip end time"
                      />
                    </div>
                    <div className="flex flex-col gap-2 sm:flex-row">
                      <button
                        type="button"
                        onClick={setStartHere}
                        disabled={!videoUrl}
                        className="flex-1 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-sm font-medium text-slate-200 transition hover:border-white/20 hover:bg-white/[0.07] disabled:opacity-40"
                      >
                        ⤓ Set start here
                      </button>
                      <button
                        type="button"
                        onClick={setEndHere}
                        disabled={!videoUrl}
                        className="flex-1 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-sm font-medium text-slate-200 transition hover:border-white/20 hover:bg-white/[0.07] disabled:opacity-40"
                      >
                        ⤒ Set end here
                      </button>
                    </div>
                    <p className="text-xs text-slate-500">
                      Playhead at {formatTime(currentTime)}
                    </p>
                  </div>
                </ControlCard>
              </Reveal>

              {/* Smart starters */}
              <Reveal delay={0.05}>
                <ControlCard title="Smart clip starters" badge="Auto">
                  {!videoUrl ? (
                    <p className="text-sm text-slate-500">
                      Upload a video to generate suggested clip ranges.
                    </p>
                  ) : (
                    <div className="grid grid-cols-1 gap-2.5">
                      {smartStarters.map((sug) => (
                        <button
                          key={sug.label}
                          type="button"
                          onClick={() => applyRange(sug.s, sug.e)}
                          className="group flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-left transition hover:border-brand/40 hover:bg-brand/10"
                        >
                          <span>
                            <span className="block text-sm font-semibold text-white">
                              {sug.label}
                            </span>
                            <span className="block text-xs text-slate-400">{sug.desc}</span>
                          </span>
                          <span className="font-mono text-xs text-brand-soft">
                            {formatTime(sug.s)}–{formatTime(sug.e)}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
                </ControlCard>
              </Reveal>

              {/* Aspect ratio */}
              <Reveal delay={0.1}>
                <ControlCard title="Aspect ratio" badge="Crop">
                  <div className="grid grid-cols-2 gap-2.5">
                    {ASPECTS.map((a) => (
                      <button
                        key={a.key}
                        type="button"
                        onClick={() => setAspect(a.key)}
                        aria-pressed={aspect === a.key}
                        className={[
                          'rounded-xl border px-3 py-3 text-left transition',
                          aspect === a.key
                            ? 'border-brand/50 bg-brand/15 shadow-glow'
                            : 'border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.07]',
                        ].join(' ')}
                      >
                        <span className="block text-sm font-bold text-white">{a.label}</span>
                        <span className="block text-[11px] text-slate-400">{a.note}</span>
                      </button>
                    ))}
                  </div>
                </ControlCard>
              </Reveal>

              {/* Filters */}
              <Reveal delay={0.12}>
                <ControlCard title="Look & filter" badge="Color">
                  <div className="flex flex-wrap gap-2">
                    {FILTERS.map((f) => (
                      <Pill
                        key={f.key}
                        active={filter === f.key}
                        onClick={() => setFilter(f.key)}
                      >
                        {f.label}
                      </Pill>
                    ))}
                  </div>
                  <div className="mt-4 flex gap-2 overflow-hidden rounded-xl">
                    {FILTERS.map((f) => (
                      <button
                        key={f.key}
                        type="button"
                        onClick={() => setFilter(f.key)}
                        aria-label={`Apply ${f.label} filter`}
                        className={[
                          'h-12 flex-1 rounded-lg border transition',
                          filter === f.key ? 'border-brand-soft' : 'border-transparent',
                        ].join(' ')}
                        style={{
                          filter: f.css,
                          backgroundImage:
                            'linear-gradient(135deg, #f59e0b 0%, #8b5cf6 50%, #22d3ee 100%)',
                        }}
                      />
                    ))}
                  </div>
                </ControlCard>
              </Reveal>

              {/* Captions */}
              <Reveal delay={0.14}>
                <ControlCard title="Caption / hook" badge="Text">
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="caption-input" className="mb-1.5 block text-sm font-medium text-slate-300">
                        Caption text
                      </label>
                      <input
                        id="caption-input"
                        type="text"
                        value={caption}
                        onChange={(e) => setCaption(e.target.value)}
                        placeholder="Type a hook your audience can't scroll past…"
                        maxLength={120}
                        className="w-full rounded-xl border border-white/10 bg-ink-900 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 focus:border-brand/50 focus:outline-none"
                      />
                    </div>

                    <div>
                      <span className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-slate-500">
                        Quick ideas
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {CAPTION_IDEAS.map((idea) => (
                          <button
                            key={idea}
                            type="button"
                            onClick={() => setCaption(idea)}
                            className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-300 transition hover:border-brand/40 hover:bg-brand/10 hover:text-white"
                          >
                            {idea}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-slate-500">
                          Style
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {CAPTION_STYLES.map((c) => (
                            <Pill
                              key={c.key}
                              active={captionStyle === c.key}
                              onClick={() => setCaptionStyle(c.key)}
                            >
                              {c.label}
                            </Pill>
                          ))}
                        </div>
                      </div>
                      <div>
                        <span className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-slate-500">
                          Position
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {CAPTION_POSITIONS.map((c) => (
                            <Pill
                              key={c.key}
                              active={captionPosition === c.key}
                              onClick={() => setCaptionPosition(c.key)}
                            >
                              {c.label}
                            </Pill>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div>
                      <div className="mb-1.5 flex items-center justify-between">
                        <label htmlFor="caption-size" className="text-sm font-medium text-slate-300">
                          Caption size
                        </label>
                        <span className="text-xs text-slate-500">{captionSize}</span>
                      </div>
                      <input
                        id="caption-size"
                        type="range"
                        min={2}
                        max={10}
                        step={1}
                        value={captionSize}
                        onChange={(e) => setCaptionSize(Number(e.target.value))}
                        aria-label="Caption size"
                      />
                    </div>
                  </div>
                </ControlCard>
              </Reveal>
            </div>
          </div>

          {/* Live filter style applied to a hidden helper keeps TS happy + documents intent */}
          <span className="sr-only">{activeFilterCss}</span>
        </section>

        <Workflow reduce={!!reduce} />
        <Faq />
      </main>

      <Footer />
    </div>
  )
}

/* -------------------------------------------------------------------------- */
/*  Sub-components                                                             */
/* -------------------------------------------------------------------------- */

function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={[
        'sticky top-0 z-50 transition-all duration-300',
        scrolled
          ? 'border-b border-white/10 bg-ink-950/80 backdrop-blur-xl'
          : 'border-b border-transparent bg-transparent',
      ].join(' ')}
    >
      <nav
        className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8"
        aria-label="Primary"
      >
        <a href="#top" className="flex items-center gap-2.5">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-brand-gradient shadow-glow">
            <svg viewBox="0 0 24 24" className="h-5 w-5 text-white" fill="currentColor">
              <path d="M9 7v10l8-5z" />
            </svg>
          </span>
          <span className="text-lg font-extrabold tracking-tight text-white">
            ClipForge<span className="text-brand-soft"> Studio</span>
          </span>
        </a>
        <div className="hidden items-center gap-8 md:flex">
          <a href="#studio" className="text-sm font-medium text-slate-300 transition hover:text-white">
            Studio
          </a>
          <a href="#workflow" className="text-sm font-medium text-slate-300 transition hover:text-white">
            Workflow
          </a>
          <a href="#faq" className="text-sm font-medium text-slate-300 transition hover:text-white">
            Help
          </a>
        </div>
        <a
          href="#studio"
          className="rounded-xl bg-brand-gradient px-4 py-2 text-sm font-bold text-white shadow-glow transition hover:brightness-110"
        >
          Open studio
        </a>
      </nav>
    </header>
  )
}

function Hero({
  reduce,
  hasVideo,
  onPickFile,
}: {
  reduce: boolean
  hasVideo: boolean
  onPickFile: (file: File | null | undefined) => void
}) {
  return (
    <section id="top" className="relative overflow-hidden px-4 pt-16 sm:px-6 sm:pt-24 lg:px-8">
      <div className="mx-auto max-w-4xl text-center">
        <motion.div
          variants={containerVariants}
          initial={reduce ? false : 'hidden'}
          animate="show"
        >
          <motion.span
            variants={itemVariants}
            className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs font-semibold text-slate-300"
          >
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
            100% in-browser · no uploads · no backend
          </motion.span>

          <motion.h1
            variants={itemVariants}
            className="mt-6 text-4xl font-black leading-[1.05] tracking-tight text-white sm:text-6xl md:text-7xl"
          >
            Turn long videos into
            <span className="block text-gradient">short-form gold.</span>
          </motion.h1>

          <motion.p
            variants={itemVariants}
            className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-slate-400 sm:text-lg"
          >
            ClipForge Studio is the premium clip editor for creators. Trim the best
            moment, crop it for any platform, drop a hook caption, grade the look, and
            export a ready-to-post clip — all without leaving your browser.
          </motion.p>

          <motion.div
            variants={itemVariants}
            className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row"
          >
            <label className="group cursor-pointer rounded-2xl bg-brand-gradient px-7 py-3.5 text-base font-bold text-white shadow-glow transition hover:brightness-110">
              {hasVideo ? 'Upload a different video' : 'Upload your video'}
              <input
                type="file"
                accept="video/*"
                className="sr-only"
                onChange={(e) => {
                  onPickFile(e.target.files?.[0])
                  document.getElementById('studio')?.scrollIntoView({ behavior: 'smooth' })
                }}
              />
            </label>
            <a
              href="#workflow"
              className="rounded-2xl border border-white/15 px-7 py-3.5 text-base font-semibold text-slate-200 transition hover:border-white/30 hover:bg-white/5"
            >
              See how it works
            </a>
          </motion.div>

          <motion.p variants={itemVariants} className="mt-4 text-xs text-slate-500">
            MP4 · WebM · MOV supported · Exports as WebM
          </motion.p>
        </motion.div>
      </div>

      {/* Floating mock frames */}
      <motion.div
        aria-hidden
        initial={reduce ? false : { opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        className="mx-auto mt-16 flex max-w-3xl items-end justify-center gap-4 sm:gap-6"
      >
        {[
          { r: '9:16', h: 'h-44 sm:h-60', w: 'w-24 sm:w-32' },
          { r: '1:1', h: 'h-36 sm:h-48', w: 'w-36 sm:w-48' },
          { r: '16:9', h: 'h-28 sm:h-36', w: 'w-44 sm:w-60' },
        ].map((m, i) => (
          <div
            key={m.r}
            className={`${m.h} ${m.w} ${reduce ? '' : 'animate-float'} glass grid place-items-center rounded-2xl border border-white/10 shadow-premium`}
            style={{ animationDelay: `${i * 0.6}s` }}
          >
            <span className="text-xs font-semibold text-slate-400">{m.r}</span>
          </div>
        ))}
      </motion.div>
    </section>
  )
}

function UploadDropzone({
  onPickFile,
}: {
  onPickFile: (file: File | null | undefined) => void
}) {
  const [dragging, setDragging] = useState(false)
  return (
    <label
      onDragOver={(e) => {
        e.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragging(false)
        onPickFile(e.dataTransfer.files?.[0])
      }}
      className={[
        'flex aspect-video w-full cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition',
        dragging
          ? 'border-brand bg-brand/10'
          : 'border-white/15 bg-white/[0.02] hover:border-white/30 hover:bg-white/[0.04]',
      ].join(' ')}
    >
      <span className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-gradient shadow-glow">
        <svg viewBox="0 0 24 24" className="h-7 w-7 text-white" fill="none" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 16V4m0 0L8 8m4-4l4 4M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" />
        </svg>
      </span>
      <span className="mt-4 text-base font-semibold text-white">
        Drop a video here, or click to browse
      </span>
      <span className="mt-1 text-sm text-slate-500">
        MP4, WebM or MOV · stays private on your device
      </span>
      <input
        type="file"
        accept="video/*"
        className="sr-only"
        onChange={(e) => onPickFile(e.target.files?.[0])}
      />
    </label>
  )
}

function ControlCard({
  title,
  badge,
  children,
}: {
  title: string
  badge?: string
  children: ReactNode
}) {
  return (
    <div className="glass rounded-3xl p-5 shadow-premium sm:p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-base font-bold text-white">{title}</h3>
        {badge && (
          <span className="rounded-full bg-white/5 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            {badge}
          </span>
        )}
      </div>
      {children}
    </div>
  )
}

function Workflow({ reduce }: { reduce: boolean }) {
  const steps = [
    {
      n: '01',
      title: 'Upload locally',
      body: 'Drop in an MP4, WebM or MOV. It loads instantly and never leaves your browser.',
    },
    {
      n: '02',
      title: 'Find the moment',
      body: 'Scrub, trim with precision sliders, or tap a smart starter to jump to the hook, highlight or closer.',
    },
    {
      n: '03',
      title: 'Style it for the feed',
      body: 'Crop to 9:16, 1:1 or 16:9, add a caption hook, and grade the look with one tap.',
    },
    {
      n: '04',
      title: 'Render & download',
      body: 'Preview the canvas output, then export a ready-to-post WebM with audio.',
    },
  ]
  return (
    <section
      id="workflow"
      className="mx-auto max-w-7xl scroll-mt-24 px-4 py-20 sm:px-6 sm:py-28 lg:px-8"
      aria-label="How it works"
    >
      <Reveal>
        <SectionHeading
          eyebrow="Workflow"
          title="From raw footage to feed-ready in four steps"
          subtitle="A focused pipeline built for the way creators actually clip."
        />
      </Reveal>

      <motion.div
        variants={containerVariants}
        initial={reduce ? false : 'hidden'}
        whileInView="show"
        viewport={{ once: true, margin: '-80px' }}
        className="mt-14 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4"
      >
        {steps.map((s) => (
          <motion.div
            key={s.n}
            variants={itemVariants}
            whileHover={reduce ? undefined : { y: -6 }}
            className="glass group rounded-3xl p-6 shadow-premium transition-colors hover:border-brand/30"
          >
            <span className="text-3xl font-black text-gradient">{s.n}</span>
            <h3 className="mt-4 text-lg font-bold text-white">{s.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">{s.body}</p>
          </motion.div>
        ))}
      </motion.div>
    </section>
  )
}

function Faq() {
  const [open, setOpen] = useState<number | null>(0)
  return (
    <section
      id="faq"
      className="mx-auto max-w-3xl scroll-mt-24 px-4 py-20 sm:px-6 sm:py-28 lg:px-8"
      aria-label="Help and frequently asked questions"
    >
      <Reveal>
        <SectionHeading
          eyebrow="Help"
          title="Questions, answered"
          subtitle="Everything you need to know about clipping in the browser."
        />
      </Reveal>

      <div className="mt-12 space-y-3">
        {FAQS.map((f, i) => {
          const isOpen = open === i
          return (
            <Reveal key={f.q} delay={i * 0.04}>
              <div className="glass overflow-hidden rounded-2xl">
                <h3>
                  <button
                    type="button"
                    onClick={() => setOpen(isOpen ? null : i)}
                    aria-expanded={isOpen}
                    className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
                  >
                    <span className="text-base font-semibold text-white">{f.q}</span>
                    <span
                      className={`grid h-7 w-7 shrink-0 place-items-center rounded-full border border-white/15 text-slate-300 transition-transform duration-300 ${
                        isOpen ? 'rotate-45' : ''
                      }`}
                      aria-hidden
                    >
                      +
                    </span>
                  </button>
                </h3>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: 'easeInOut' }}
                    >
                      <p className="px-5 pb-5 text-sm leading-relaxed text-slate-400">{f.a}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </Reveal>
          )
        })}
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="border-t border-white/10 bg-ink-950/60">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col items-start justify-between gap-8 md:flex-row md:items-center">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-gradient">
                <svg viewBox="0 0 24 24" className="h-4 w-4 text-white" fill="currentColor">
                  <path d="M9 7v10l8-5z" />
                </svg>
              </span>
              <span className="text-base font-extrabold text-white">ClipForge Studio</span>
            </div>
            <p className="mt-3 max-w-sm text-sm text-slate-500">
              The private, in-browser clip editor for creators. No accounts, no uploads,
              no waiting on a render farm.
            </p>
          </div>
          <nav className="flex flex-wrap gap-x-8 gap-y-3 text-sm" aria-label="Footer">
            <a href="#studio" className="text-slate-400 transition hover:text-white">Studio</a>
            <a href="#workflow" className="text-slate-400 transition hover:text-white">Workflow</a>
            <a href="#faq" className="text-slate-400 transition hover:text-white">Help</a>
            <a href="#top" className="text-slate-400 transition hover:text-white">Back to top</a>
          </nav>
        </div>
        <div className="mt-10 border-t border-white/5 pt-6 text-center text-xs text-slate-600">
          © {new Date().getFullYear()} ClipForge Studio · Runs entirely in your browser ·
          Exports WebM
        </div>
      </div>
    </footer>
  )
}
