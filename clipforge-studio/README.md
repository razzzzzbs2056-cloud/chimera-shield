# 🎬 ClipForge Studio

A premium, **100% in-browser** video clipping and editing app for social media
creators. Upload a video, find the best moment, crop it for any platform, add a
hook caption, grade the look, preview the result on a live canvas, and export a
ready-to-post clip — all without a backend. Your footage never leaves your
device.

> Built with **React + Vite + TypeScript + Tailwind CSS + Framer Motion**. The
> entire app lives in [`src/App.tsx`](./src/App.tsx).

---

## ✨ Features

| | |
|---|---|
| **Local upload** | Drag-and-drop or browse for MP4 / WebM / MOV. Loaded as a local object URL — no upload, no server. |
| **Source monitor** | Native video playback with full controls. |
| **Precision trimming** | Start/End range sliders, formatted timestamps, and “Set start here” / “Set end here” buttons based on the playhead. |
| **Smart clip starters** | One-tap suggested ranges: Opening hook, Mid-video highlight, Closing punch. |
| **Social aspect ratios** | 9:16 (TikTok/Reels/Shorts), 1:1 (feed), 16:9 (YouTube/X/LinkedIn), or Original — with center-crop. |
| **Captions** | Text input, Glass / Bold / Minimal styles, Top / Center / Bottom position, size slider, and quick caption ideas. |
| **Visual filters** | Clean, Cinematic, Vibrant, Noir, Warm. |
| **Canvas output preview** | Live canvas rendering the cropped video + filter + caption + progress overlay. |
| **Clip preview** | “Preview selected clip” plays only the trimmed start→end range. |
| **Export** | Renders the canvas via `canvas.captureStream` + `MediaRecorder` to a downloadable **WebM**, including audio when the browser supports `video.captureStream` audio tracks. |

---

## 🚀 Getting started

```bash
cd clipforge-studio
npm install
npm run dev      # start the dev server (Vite)
```

Then open the printed local URL.

### Build for production

```bash
npm run build    # type-check + production build into dist/
npm run preview  # preview the production build locally
```

---

## 🎞️ A note on export format (WebM vs MP4)

Browsers can record canvas output to **WebM** natively through the
`MediaRecorder` API. True **MP4 (H.264)** encoding is **not** exposed to the
browser, so producing an MP4 requires either:

- **Server-side encoding** (e.g. an `ffmpeg` backend), or
- A heavier **WebAssembly encoder** in the browser (e.g. `ffmpeg.wasm`), which
  significantly increases bundle size and render time.

WebM is widely supported and uploads cleanly to TikTok, Instagram Reels,
YouTube Shorts, YouTube, and X. If you need MP4 specifically, add a conversion
step downstream.

---

## ♿ Accessibility & UX

- Semantic landmarks (`header`, `main`, `nav`, `section`, `footer`) and labelled inputs.
- Visible `:focus-visible` rings throughout.
- Respects `prefers-reduced-motion` (animations and smooth scroll are disabled).
- Mobile-first, fully responsive layout.
- Safe, human-readable error messages for upload, playback, and export failures.
- Rendering is blocked until a video is uploaded.

---

## 🧱 Tech stack

- [React 18](https://react.dev/) + [Vite 5](https://vitejs.dev/)
- [TypeScript](https://www.typescriptlang.org/) (strict mode)
- [Tailwind CSS](https://tailwindcss.com/)
- [Framer Motion](https://www.framer.com/motion/)

All editing — trimming, cropping, captioning, filtering, and rendering — runs
client-side using the HTML5 `<video>` element, the Canvas 2D API, and
`MediaRecorder`.
