import { useMemo, useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import * as THREE from "three";

// ============================================
// THE CONNECTOME
// 800 nodes in a sphere · proximity synapses
// additive glow · Bloom · OrbitControls
// 60fps: 2 draw calls (Points + LineSegments)
// ============================================

const PARTICLE_COUNT = 800;
const PROXIMITY = 0.42;
const SYNAPSE_LIMIT_PER_NODE = 4;
const RADIUS = 1.6;

const PALETTE = [
  new THREE.Color("#00E5FF"),
  new THREE.Color("#3DB8FF"),
  new THREE.Color("#7C5BFF"),
  new THREE.Color("#00FFB8"),
  new THREE.Color("#A8FFFB"),
];

function mulberry32(seed: number) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

type Particle = {
  pos: THREE.Vector3;
  color: THREE.Color;
  size: number;
  speed: number;
  phase: number;
};

function generateParticles(): Particle[] {
  const rand = mulberry32(42);
  const arr: Particle[] = [];
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    let x = 0, y = 0, z = 0, r2 = 0;
    do {
      x = (rand() * 2 - 1) * RADIUS;
      y = (rand() * 2 - 1) * RADIUS;
      z = (rand() * 2 - 1) * RADIUS;
      r2 = x * x + y * y + z * z;
    } while (r2 > RADIUS * RADIUS);
    arr.push({
      pos: new THREE.Vector3(x, y, z),
      color: PALETTE[Math.floor(rand() * PALETTE.length)],
      size: 0.014 + rand() * 0.024,
      speed: 0.2 + rand() * 0.5,
      phase: rand() * Math.PI * 2,
    });
  }
  return arr;
}

type Edge = { a: number; b: number; dist: number };

function buildEdges(particles: Particle[]): Edge[] {
  const edges: Edge[] = [];
  const prox2 = PROXIMITY * PROXIMITY;
  for (let i = 0; i < particles.length; i++) {
    const a = particles[i].pos;
    const candidates: { j: number; d2: number }[] = [];
    for (let j = i + 1; j < particles.length; j++) {
      const b = particles[j].pos;
      const dx = a.x - b.x, dy = a.y - b.y, dz = a.z - b.z;
      const d2 = dx * dx + dy * dy + dz * dz;
      if (d2 < prox2) candidates.push({ j, d2 });
    }
    candidates.sort((p, q) => p.d2 - q.d2);
    const take = Math.min(candidates.length, SYNAPSE_LIMIT_PER_NODE);
    for (let k = 0; k < take; k++) {
      edges.push({ a: i, b: candidates[k].j, dist: Math.sqrt(candidates[k].d2) });
    }
  }
  return edges;
}

// ============================================
// SHADERS
// ============================================
const NODE_VERT = /* glsl */ `
  attribute float aSize;
  attribute float aPhase;
  attribute float aSpeed;
  attribute vec3 aColor;
  uniform float uTime;
  uniform float uPixelRatio;
  varying vec3 vColor;
  varying float vPulse;
  void main() {
    vec3 p = position;
    p.x += sin(uTime * aSpeed + aPhase) * 0.03;
    p.y += cos(uTime * aSpeed * 0.7 + aPhase) * 0.03;
    p.z += sin(uTime * aSpeed * 0.5 + aPhase * 1.3) * 0.03;
    vec4 mv = modelViewMatrix * vec4(p, 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = aSize * 220.0 * uPixelRatio / -mv.z;
    vColor = aColor;
    vPulse = 0.55 + 0.45 * sin(uTime * aSpeed * 1.5 + aPhase);
  }
`;
const NODE_FRAG = /* glsl */ `
  precision highp float;
  varying vec3 vColor;
  varying float vPulse;
  void main() {
    vec2 c = gl_PointCoord - 0.5;
    float d = length(c);
    if (d > 0.5) discard;
    float core = smoothstep(0.5, 0.0, d);
    float halo = pow(core, 2.4);
    vec3 col = vColor * (1.4 + vPulse * 1.6);
    gl_FragColor = vec4(col * (halo + 0.3 * core), core);
  }
`;

const LINE_VERT = /* glsl */ `
  attribute float aAlpha;
  attribute vec3 aColor;
  varying float vAlpha;
  varying vec3 vColor;
  void main() {
    vAlpha = aAlpha;
    vColor = aColor;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;
const LINE_FRAG = /* glsl */ `
  precision highp float;
  varying float vAlpha;
  varying vec3 vColor;
  void main() {
    gl_FragColor = vec4(vColor * 1.6, vAlpha);
  }
`;

// ============================================
// NODE CLOUD (1 draw call)
// ============================================
function Nodes({ particles }: { particles: Particle[] }) {
  const matRef = useRef<THREE.ShaderMaterial>(null!);
  const { gl } = useThree();
  const dpr = gl.getPixelRatio();

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(particles.length * 3);
    const col = new Float32Array(particles.length * 3);
    const sizes = new Float32Array(particles.length);
    const phases = new Float32Array(particles.length);
    const speeds = new Float32Array(particles.length);
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      pos[i * 3] = p.pos.x;
      pos[i * 3 + 1] = p.pos.y;
      pos[i * 3 + 2] = p.pos.z;
      col[i * 3] = p.color.r;
      col[i * 3 + 1] = p.color.g;
      col[i * 3 + 2] = p.color.b;
      sizes[i] = p.size;
      phases[i] = p.phase;
      speeds[i] = p.speed;
    }
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    geo.setAttribute("aColor", new THREE.BufferAttribute(col, 3));
    geo.setAttribute("aSize", new THREE.BufferAttribute(sizes, 1));
    geo.setAttribute("aPhase", new THREE.BufferAttribute(phases, 1));
    geo.setAttribute("aSpeed", new THREE.BufferAttribute(speeds, 1));
    return geo;
  }, [particles]);

  useFrame(({ clock }) => {
    if (matRef.current) {
      matRef.current.uniforms.uTime.value = clock.getElapsedTime();
    }
  });

  return (
    <points geometry={geometry}>
      <shaderMaterial
        ref={matRef}
        vertexShader={NODE_VERT}
        fragmentShader={NODE_FRAG}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        uniforms={{ uTime: { value: 0 }, uPixelRatio: { value: dpr } }}
      />
    </points>
  );
}

// ============================================
// SYNAPSES (1 draw call)
// ============================================
function Synapses({ particles, edges }: { particles: Particle[]; edges: Edge[] }) {
  const matRef = useRef<THREE.ShaderMaterial>(null!);

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    const verts = new Float32Array(edges.length * 6);
    const cols = new Float32Array(edges.length * 6);
    const alphas = new Float32Array(edges.length * 2);
    for (let i = 0; i < edges.length; i++) {
      const e = edges[i];
      const a = particles[e.a];
      const b = particles[e.b];
      verts[i * 6 + 0] = a.pos.x;
      verts[i * 6 + 1] = a.pos.y;
      verts[i * 6 + 2] = a.pos.z;
      verts[i * 6 + 3] = b.pos.x;
      verts[i * 6 + 4] = b.pos.y;
      verts[i * 6 + 5] = b.pos.z;
      const cr = (a.color.r + b.color.r) * 0.5 * 0.6 + 0.25;
      const cg = (a.color.g + b.color.g) * 0.5 * 0.8 + 0.45;
      const cb = (a.color.b + b.color.b) * 0.5 * 0.9 + 0.55;
      cols[i * 6 + 0] = cr; cols[i * 6 + 1] = cg; cols[i * 6 + 2] = cb;
      cols[i * 6 + 3] = cr; cols[i * 6 + 4] = cg; cols[i * 6 + 5] = cb;
      const fade = 1 - e.dist / PROXIMITY;
      const alpha = 0.18 + fade * fade * 0.55;
      alphas[i * 2 + 0] = alpha;
      alphas[i * 2 + 1] = alpha;
    }
    geo.setAttribute("position", new THREE.BufferAttribute(verts, 3));
    geo.setAttribute("aColor", new THREE.BufferAttribute(cols, 3));
    geo.setAttribute("aAlpha", new THREE.BufferAttribute(alphas, 1));
    return geo;
  }, [particles, edges]);

  useFrame(({ clock }) => {
    if (matRef.current) {
      (matRef.current.uniforms as any).uTime.value = clock.getElapsedTime();
    }
  });

  return (
    <lineSegments geometry={geometry}>
      <shaderMaterial
        ref={matRef}
        vertexShader={LINE_VERT}
        fragmentShader={LINE_FRAG}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        uniforms={{ uTime: { value: 0 } }}
      />
    </lineSegments>
  );
}

// ============================================
// CONNECTOME GROUP — auto-rotates
// ============================================
function ConnectomeGroup({ particles, edges }: { particles: Particle[]; edges: Edge[] }) {
  const groupRef = useRef<THREE.Group>(null!);
  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.12;
      groupRef.current.rotation.x += delta * 0.04;
    }
  });
  return (
    <group ref={groupRef}>
      <Nodes particles={particles} />
      <Synapses particles={particles} edges={edges} />
    </group>
  );
}

// ============================================
// EXPORT
// ============================================
export function Connectome() {
  const particles = useMemo(() => generateParticles(), []);
  const edges = useMemo(() => buildEdges(particles), [particles]);

  return (
    <Canvas
      camera={{ position: [0, 0, 4.2], fov: 55, near: 0.1, far: 50 }}
      dpr={[1, 1.5]}
      gl={{
        antialias: true,
        powerPreference: "high-performance",
        alpha: false,
      }}
      onCreated={({ gl, scene }) => {
        gl.setClearColor(new THREE.Color("#050505"), 1);
        scene.fog = new THREE.FogExp2("#050505", 0.06);
      }}
    >
      <ambientLight intensity={0.4} />
      <pointLight position={[5, 5, 5]} intensity={0.4} color="#00E5FF" />
      <ConnectomeGroup particles={particles} edges={edges} />
      <OrbitControls
        enableDamping
        dampingFactor={0.08}
        enablePan
        enableZoom
        enableRotate
        minDistance={1.6}
        maxDistance={12}
        rotateSpeed={0.5}
        zoomSpeed={0.6}
        panSpeed={0.4}
      />
      <EffectComposer multisampling={0}>
        <Bloom
          intensity={1.4}
          luminanceThreshold={0.05}
          luminanceSmoothing={0.9}
          mipmapBlur
          radius={0.85}
        />
      </EffectComposer>
    </Canvas>
  );
}

export const CONNECTOME_STATS = {
  nodes: PARTICLE_COUNT,
  proximity: PROXIMITY,
  radius: RADIUS,
  get edges() {
    return buildEdges(generateParticles()).length;
  },
};
