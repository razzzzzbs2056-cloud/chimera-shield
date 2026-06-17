/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL for the optional AI backend (e.g. http://localhost:8000). Empty = same-origin / dev proxy. */
  readonly VITE_AI_API_BASE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
