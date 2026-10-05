"use client";

import { useCallback, useMemo, useState } from "react";
import type { BimElement } from "@/lib/engine/types";
import { BimViewer } from "./bim-viewer";
import { SERIES } from "./charts";

type Act = { id: string; name: string; es: number; ef: number; levels?: number[] };

/** 4D BIM: elements are linked to their activity (structure/façade/MEP/fit-out per level) and coloured by state on the chosen day. */
export function Construction4D({ projectId, acts, total }: { projectId: string; acts: Act[]; total: number }) {
  const [day, setDay] = useState(Math.round(total * 0.45));
  const byLevel = useMemo(() => {
    const m = new Map<string, Act>();
    acts.forEach((a) => a.levels?.forEach((l) => m.set(`${a.id[0]}${l}`, a)));
    return m;
  }, [acts]);
  const builtLevel = useMemo(() => {
    let lvl = -1;
    acts.filter((a) => a.id.startsWith("S")).forEach((a) => { if (a.es <= day && a.levels) lvl = Math.max(lvl, ...a.levels); });
    return lvl;
  }, [acts, day]);
  const color = useCallback((e: BimElement) => {
    const key = e.discipline === "ARC" && e.ifc === "IfcPlate" ? "F" : e.discipline === "STR" || e.ifc === "IfcStair" ? "S" : "M";
    const a = byLevel.get(`${key}${e.level}`);
    if (!a) return e.discipline === "STR" ? "#94a3b8" : "#cbd5e1";
    if (day < a.es) return null;
    if (day < a.ef) return SERIES[1]; // in progress
    return key === "S" ? "#94a3b8" : key === "F" ? SERIES[0] : SERIES[2];
  }, [byLevel, day]);
  const month = Math.floor(day / 21.7) + 1;
  return (
    <div>
      <label className="mb-3 block">
        <span className="label flex justify-between"><span>Programme day {day} (month {month})</span><span>{builtLevel + 1} levels of structure started</span></span>
        <input type="range" min={0} max={total} value={day} onChange={(e) => setDay(+e.target.value)} className="w-full accent-brand-600" aria-label="Programme day" />
      </label>
      <BimViewer projectId={projectId} mode="4d" progressLevel={builtLevel} phaseColor={color} height={420} />
      <div className="mt-2 flex flex-wrap gap-3 text-[11px] text-slate-600">
        <span className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: SERIES[1] }} />In progress</span>
        <span className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm bg-slate-400" />Structure complete</span>
        <span className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: SERIES[0] }} />Façade installed</span>
        <span className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: SERIES[2] }} />Services installed</span>
      </div>
    </div>
  );
}
