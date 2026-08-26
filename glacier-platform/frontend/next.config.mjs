/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // The backend API base is read at runtime by the browser via NEXT_PUBLIC_API_BASE.
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000",
  },
};
export default nextConfig;
