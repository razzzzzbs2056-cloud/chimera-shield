import { Skeleton } from "@/components/ui";

export default function Loading() {
  return (
    <div className="space-y-5" aria-busy>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">{Array.from({ length: 4 }, (_, i) => <Skeleton key={i} className="h-24" />)}</div>
      <div className="grid gap-4 lg:grid-cols-2"><Skeleton className="h-80" /><Skeleton className="h-80" /></div>
      <Skeleton className="h-64" />
    </div>
  );
}
