# POST /api/v1/analyze — request

| Field | Type | Notes |
|---|---|---|
| `buildingType` | `office · residential · hospital · school · retail · mixed-use · laboratory · hotel · warehouse` | default `office` |
| `city` | preset city (San Francisco, Los Angeles, Seattle, New York, Boston, Chicago, Austin, Houston, London, Manchester, Sydney, Melbourne, Auckland, Wellington, Singapore, Toronto, Vancouver) | fills climate & hazard data |
| `floors` | 1–90 | storeys above grade |
| `agents` | array of agent IDs | sections to return; default `["codes","verifier"]` |
| `intake` | object | overrides: `siteWidth`, `siteDepth`, `budget`, `targetEUI`, `targetCarbon`, `Ss`, `S1`, `basicWindSpeed`, `exposure`, `floodZone`, `parkingSpaces`, `priorities{cost,carbon,area,daylight,speed}` … |
| `params` | object | design overrides: `material`, `lateralSystem`, `slabSystem`, `spanX`, `spanY`, `coreWidth`, `wwr`, `facadeType`, `heating` … |
| `boreholes` | array | `{name, x, y, gwl, layers:[{top,bottom,soil,spt,gamma,cu?,phi?,Es,cc?,e0?,finesPct?}]}` |
| `pins` | object | pin code editions, e.g. `{"ASCE 7":"7-16"}` |

# Response

`kpis` (cost, carbon, EUI, drift, programme, pass/fail counts…), `system`, `params` (after agent changes), `changes`, `failing` (clause-level FAIL findings), `agents.<id>` (result sections), `usage`, `disclaimer`.
