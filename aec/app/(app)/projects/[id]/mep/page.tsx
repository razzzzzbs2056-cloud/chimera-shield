import { BarViz } from "@/components/charts";
import { NoRun } from "@/components/no-run";
import { KV, SectionTitle } from "@/components/page";
import { Card, Stat, StatusBadge, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function Mep({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const h = run.hvac, e = run.electrical, w = run.hydraulics;
  return (
    <>
      <SectionTitle sub="Loads, ventilation, plant, ducts and comfort">HVAC design engine</SectionTitle>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Peak cooling" value={fmt.n(h.coolingPeak)} unit="kW" hint={`${h.coolingWm2} W/m² GFA`} />
        <Stat label="Peak heating" value={fmt.n(h.heatingPeak)} unit="kW" hint={`${h.heatingWm2} W/m² GFA`} />
        <Stat label="Outdoor air" value={h.oa} unit="m³/s" hint={`${h.oaPerPerson} L/s per person (ASHRAE 62.1)`} />
        <Stat label="Comfort (summer PMV)" value={h.comfort.summer.PMV} hint={`PPD ${h.comfort.summer.PPD}% · winter PMV ${h.comfort.winter.PMV}`} tone={Math.abs(h.comfort.summer.PMV) <= 0.5 ? "good" : "warn"} />
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Cooling load breakdown" subtitle="Building peak by component (kW)" className="lg:col-span-2"><BarViz data={h.breakdown.map((b) => ({ name: b.name, kW: b.kW }))} x="name" series={[{ key: "kW" }]} height={240} /></Card>
        <Card title="Central plant">
          <KV cols={1} rows={[["Chillers", `${h.plant.chillers} × ${h.plant.chillerSize} kW (${h.plant.redundancy})`], ["Cooling towers", h.plant.towers], [run.params.heating === "heat-pump" ? "Heat pumps" : "Boilers", run.params.heating === "heat-pump" ? h.plant.heatPumps : `${h.plant.boilers} × ${h.plant.boilerSize} kW`], ["AHUs", `${h.plant.ahus} × ${h.plant.ahuSize} m³/s`], ["Plant room", `${h.plant.plantArea} m²`], ["Riser area", `${h.plant.riserArea} m²`], ["Main duct", `Ø${Math.round(h.ducts.mainDiameter * 1000)} mm eq. @ ${h.ducts.mainVelocity} m/s`], ["Riser duct", `Ø${Math.round(h.ducts.riserDiameter * 1000)} mm`], ["Ceiling void", `${h.ducts.ceilingVoid} m`], ["Fans / pumps", `${h.fanPower} / ${h.pumpPower} kW`]]} />
        </Card>
      </div>
      <Card title="Zoning — typical floor" pad={false}>
        <Table head={["Zone", "Area (m²)", "Sensible (kW)", "Latent (kW)", "Supply air (L/s)", "W/m²"]}>
          {h.zones.map((z) => <tr key={z.name}><td className="td">{z.name}</td><td className="td num">{fmt.n(z.area)}</td><td className="td num">{z.sensible}</td><td className="td num">{z.latent}</td><td className="td num">{fmt.n(z.airflow)}</td><td className="td num">{z.wPerM2}</td></tr>)}
        </Table>
      </Card>

      <SectionTitle sub="Load schedule, transformers, cables, protection, renewables and emergency power">Electrical design engine</SectionTitle>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Maximum demand" value={fmt.n(e.maxDemandKVA)} unit="kVA" hint={`${fmt.n(e.maxDemandKW)} kW @ pf ${e.pf} · ${e.vaPerM2} VA/m²`} />
        <Stat label="Transformers" value={e.transformers.config} hint={`Utilisation ${Math.round(e.transformers.utilisation * 100)}%`} tone={e.transformers.utilisation > 0.8 ? "warn" : "good"} />
        <Stat label="Rooftop PV" value={fmt.n(e.pv.kWp)} unit="kWp" hint={`${fmt.n(e.pv.annual)} MWh/yr · ${e.pv.share}% of demand`} />
        <Stat label="Standby generator" value={fmt.n(e.generator.kVA)} unit="kVA" hint={`${e.generator.fuelHours} h fuel · BESS ${fmt.n(e.battery.kWh)} kWh`} />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Load schedule" pad={false}>
          <Table head={["Load", "Connected (kW)", "Demand factor", "Demand (kW)"]}>
            {e.schedule.map((r) => <tr key={r.load}><td className="td">{r.load}</td><td className="td num">{fmt.n(r.connected)}</td><td className="td num">{r.demandFactor}</td><td className="td num">{fmt.n(r.demand)}</td></tr>)}
          </Table>
        </Card>
        <Card title="Sub-mains, cable sizing & voltage drop" subtitle={`Main switchboard ${e.mainSwitchboard.rating} A, prospective fault ${e.mainSwitchboard.faultKA} kA`} pad={false}>
          <Table head={["Circuit", "Length", "Current", "Cable", "VD", "Breaker"]}>
            {e.risers.map((r) => <tr key={r.name}><td className="td">{r.name}</td><td className="td num">{r.length} m</td><td className="td num">{r.current} A</td><td className="td">{r.parallel > 1 ? `${r.parallel}× ` : ""}{r.cable}</td><td className="td"><StatusBadge status={r.vd <= 3 ? "PASS" : "FAIL"} label={`${r.vd}%`} /></td><td className="td num">{r.breaker} A</td></tr>)}
          </Table>
          <div className="p-4"><KV rows={[["EV chargers", `${e.ev.chargers} × 7.4 kW (managed to ${e.ev.managedKW} kW)`], ["Battery storage", `${e.battery.kWh} kWh / ${e.battery.kW} kW`], ["Life-safety load", `${e.generator.lifeSafetyKW} kW`], ["Standby load", `${e.generator.standbyKW} kW`]]} /></div>
        </Card>
      </div>

      <SectionTitle sub="Water, sewer, stormwater, pumps, hot water, rainwater & greywater">Hydraulic design engine</SectionTitle>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Fixtures & drainage" pad={false}>
          <Table head={["Fixture", "Count", "WSFU", "DFU"]}>{w.fixtures.map((f) => <tr key={f.type}><td className="td">{f.type}</td><td className="td num">{f.count}</td><td className="td num">{f.wsfu}</td><td className="td num">{f.dfu}</td></tr>)}</Table>
          <div className="p-4"><KV cols={1} rows={[["Total WSFU / DFU", `${w.wsfu} / ${w.dfu}`], ["Soil stack", `DN${Math.round(w.stackDiameter * 1000)}`], ["Building drain", `DN${Math.round(w.buildingDrain * 1000)}`]]} /></div>
        </Card>
        <Card title="Water supply & pumping">
          <KV cols={1} rows={[["Peak flow (Hunter)", `${w.peakFlow} L/s`], ["Main", `DN${Math.round(w.mainDiameter * 1000)} @ ${w.velocity} m/s`], ["Daily demand", `${w.dailyDemand} m³`], ["Pressure zones", w.pressureZones], ["Booster pumps", w.boosterRequired ? `${w.boosterKW} kW, ${w.boosterHead} kPa` : "Not required"], ["Hot-water storage", `${fmt.n(w.dhw.storage)} L`], ["Water heater", `${w.dhw.heaterKW} kW`], ["Recirculation", w.dhw.recirculation ? "Yes" : "No"]]} />
        </Card>
        <Card title="Stormwater & reuse">
          <KV cols={1} rows={[["Roof area", `${fmt.n(w.storm.roofArea)} m²`], ["Design flow (Q = CiA)", `${w.storm.flow} L/s`], ["Roof drains", `${w.storm.drains} × DN${w.storm.drainSize} + overflows`], ["On-site detention", `${w.storm.detention} m³`], ["Rainwater yield", `${fmt.n(w.rainwater.annualYield)} m³/yr`], ["Rainwater tank", `${fmt.n(w.rainwater.tank)} m³`], ["Flushing offset (rain)", `${w.rainwater.demandOffset}%`], ["Greywater", `${w.greywater.daily} m³/day (${w.greywater.flushingOffset}% of flushing)`]]} />
        </Card>
      </div>
    </>
  );
}
