import { NextResponse } from "next/server";
import { AGENTS, PLANS } from "@/lib/agent-catalog";
import { ENGINE_VERSION } from "@/lib/engine/workflow";

// Public catalog — no key required.
export function GET() {
  return NextResponse.json({ engineVersion: ENGINE_VERSION, agents: AGENTS, plans: PLANS });
}
