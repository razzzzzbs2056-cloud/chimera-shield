import Link from "next/link";

export default function NotFound() {
  return <div className="py-20 text-center"><h2 className="text-lg font-semibold">Project not found</h2><p className="mt-1 text-sm text-slate-500">It may have been deleted or belongs to another workspace.</p><Link href="/projects" className="mt-4 inline-block text-sm font-medium text-brand-700 hover:underline">Back to projects</Link></div>;
}
