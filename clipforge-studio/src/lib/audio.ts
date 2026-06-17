/**
 * In-browser smart auto-edit helpers.
 *
 * Everything here runs locally using the Web Audio API — no backend, no AI
 * service. We decode the uploaded file's audio track, measure loudness over
 * short windows, and use that energy envelope to:
 *   - suggest highlight clip ranges (the loudest, most "eventful" moments), and
 *   - trim leading / trailing silence.
 *
 * This is heuristic, not machine learning, but it's fast, private, and works
 * offline — exactly what a creator wants for a first pass.
 */

export interface AudioAnalysis {
  /** RMS loudness per window, normalised 0..1. */
  envelope: number[]
  /** Seconds covered by each envelope sample. */
  windowSec: number
  /** Total decoded duration in seconds. */
  duration: number
}

export interface ClipRange {
  start: number
  end: number
}

const WINDOW_SEC = 0.4

/** Decode a video/audio File and compute a normalised loudness envelope. */
export async function analyzeAudio(file: File): Promise<AudioAnalysis> {
  const arrayBuffer = await file.arrayBuffer()
  const AudioCtx: typeof AudioContext =
    window.AudioContext ||
    (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext
  if (!AudioCtx) throw new Error('Web Audio API is not supported in this browser.')

  const ctx = new AudioCtx()
  let audioBuffer: AudioBuffer
  try {
    audioBuffer = await ctx.decodeAudioData(arrayBuffer)
  } finally {
    // Free the context regardless of success.
    void ctx.close()
  }

  const channel = audioBuffer.getChannelData(0)
  const sampleRate = audioBuffer.sampleRate
  const windowSize = Math.max(1, Math.floor(sampleRate * WINDOW_SEC))

  const raw: number[] = []
  for (let i = 0; i < channel.length; i += windowSize) {
    let sumSq = 0
    let n = 0
    const end = Math.min(i + windowSize, channel.length)
    for (let j = i; j < end; j++) {
      sumSq += channel[j] * channel[j]
      n++
    }
    raw.push(Math.sqrt(sumSq / Math.max(1, n)))
  }

  const max = Math.max(...raw, 1e-6)
  const envelope = raw.map((v) => v / max)

  return { envelope, windowSec: WINDOW_SEC, duration: audioBuffer.duration }
}

/**
 * Suggest up to `count` highlight ranges centred on the loudest moments,
 * spaced apart so they don't overlap. Each range is padded for context.
 */
export function findHighlights(
  analysis: AudioAnalysis,
  count = 3,
  clipLength = 14,
): ClipRange[] {
  const { envelope, windowSec, duration } = analysis
  if (!envelope.length) return []

  const indexed = envelope.map((energy, i) => ({ energy, t: i * windowSec }))
  indexed.sort((a, b) => b.energy - a.energy)

  const picks: { t: number }[] = []
  const minGap = clipLength * 0.8
  for (const candidate of indexed) {
    if (picks.length >= count) break
    if (picks.some((p) => Math.abs(p.t - candidate.t) < minGap)) continue
    picks.push({ t: candidate.t })
  }

  const lead = clipLength * 0.35
  return picks
    .sort((a, b) => a.t - b.t)
    .map(({ t }) => {
      const start = Math.max(0, t - lead)
      const end = Math.min(duration, start + clipLength)
      return { start, end }
    })
}

/** Find the first and last moments above a loudness threshold (trim silence). */
export function trimSilence(analysis: AudioAnalysis, threshold = 0.12): ClipRange {
  const { envelope, windowSec, duration } = analysis
  if (!envelope.length) return { start: 0, end: duration }

  let first = 0
  while (first < envelope.length && envelope[first] < threshold) first++
  let last = envelope.length - 1
  while (last > 0 && envelope[last] < threshold) last--

  if (first >= last) return { start: 0, end: duration }
  return {
    start: Math.max(0, first * windowSec),
    end: Math.min(duration, (last + 1) * windowSec),
  }
}
