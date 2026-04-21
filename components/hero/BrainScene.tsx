'use client';

import { useRef, useState, useEffect, useMemo, useCallback } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';
import gsap from 'gsap';

// ─── Geometry utilities ───────────────────────────────────────────────────────

function buildBrainGeometry(): THREE.BufferGeometry {
  const geo = new THREE.IcosahedronGeometry(1.8, 4);
  const pos = geo.attributes.position as THREE.BufferAttribute;

  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const y = pos.getY(i);
    const z = pos.getZ(i);
    const r = Math.hypot(x, y, z);
    if (r === 0) continue;
    const nx = x / r, ny = y / r, nz = z / r;
    const theta = Math.acos(Math.max(-1, Math.min(1, ny)));
    const phi = Math.atan2(nz, nx);

    const d =
      0.24 * Math.sin(3 * theta) * Math.cos(2 * phi) +
      0.13 * Math.sin(6 * theta) * Math.cos(5 * phi) +
      0.07 * Math.sin(10 * theta) * Math.cos(9 * phi) +
      0.03 * Math.sin(17 * theta) * Math.cos(14 * phi);

    const newR = r + d;
    pos.setXYZ(i, nx * newR * 0.9, ny * newR * 0.82, nz * newR);
  }

  geo.computeVertexNormals();
  return geo;
}

function pickSynapses(geo: THREE.BufferGeometry, count: number): THREE.Vector3[] {
  const pos = geo.attributes.position as THREE.BufferAttribute;
  const map = new Map<string, THREE.Vector3>();

  for (let i = 0; i < pos.count; i++) {
    const v = new THREE.Vector3(pos.getX(i), pos.getY(i), pos.getZ(i));
    const key = `${(v.x * 60) | 0},${(v.y * 60) | 0},${(v.z * 60) | 0}`;
    if (!map.has(key)) map.set(key, v);
  }

  const verts = [...map.values()];
  verts.sort((a, b) => b.lengthSq() - a.lengthSq());
  const pool = verts.slice(0, Math.ceil(verts.length * 0.65));
  const step = Math.floor(pool.length / count);
  return pool.filter((_, i) => i % step === 0).slice(0, count);
}

// ─── Silver wireframe ─────────────────────────────────────────────────────────

function BrainWireframe({ geo }: { geo: THREE.BufferGeometry }) {
  const matRef = useRef<THREE.LineBasicMaterial>(null!);
  const wireGeo = useMemo(() => new THREE.WireframeGeometry(geo), [geo]);

  useFrame(({ clock }) => {
    if (matRef.current)
      matRef.current.opacity = 0.22 + 0.05 * Math.sin(clock.elapsedTime * 0.45);
  });

  return (
    <lineSegments geometry={wireGeo}>
      <lineBasicMaterial ref={matRef} color="#5878A8" transparent opacity={0.22} />
    </lineSegments>
  );
}

// ─── Golden synapse nodes ─────────────────────────────────────────────────────

function SynapseNode({
  position,
  prominent,
  onClick,
}: {
  position: THREE.Vector3;
  prominent: boolean;
  onClick?: () => void;
}) {
  const meshRef = useRef<THREE.Mesh>(null!);
  const matRef = useRef<THREE.MeshStandardMaterial>(null!);

  const radius = useMemo(
    () =>
      prominent
        ? 0.062
        : 0.021 + Math.abs(Math.sin(position.x * 47.3 + position.z * 31.1)) * 0.016,
    [position, prominent],
  );

  const phase = position.x * 3.7 + position.y * 2.1 + position.z * 1.4;

  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    if (!matRef.current) return;
    matRef.current.emissiveIntensity =
      (prominent ? 2.8 : 1.1) + Math.sin(t * 1.6 + phase) * 0.7;
    if (prominent && meshRef.current) {
      meshRef.current.scale.setScalar(1 + 0.1 * Math.sin(t * 2.4 + phase));
    }
  });

  return (
    <mesh
      ref={meshRef}
      position={position}
      onClick={prominent ? onClick : undefined}
      onPointerOver={() => { if (prominent) document.body.style.cursor = 'pointer'; }}
      onPointerOut={() => { document.body.style.cursor = 'auto'; }}
    >
      <sphereGeometry args={[radius, 14, 14]} />
      <meshStandardMaterial
        ref={matRef}
        color={prominent ? '#FFD060' : '#C49020'}
        emissive={prominent ? '#FFAA00' : '#A07010'}
        emissiveIntensity={prominent ? 2.8 : 1.1}
        metalness={0.5}
        roughness={0.15}
      />
    </mesh>
  );
}

// ─── Fiber-optic neural pathways ──────────────────────────────────────────────

function FiberOpticPaths({
  origin,
  visible,
}: {
  origin: THREE.Vector3 | null;
  visible: boolean;
}) {
  const matsRef = useRef<(THREE.MeshStandardMaterial | null)[]>([]);

  const tubes = useMemo(() => {
    if (!origin) return [];

    const dir = origin.clone().normalize();
    const worldUp =
      Math.abs(dir.y) < 0.9
        ? new THREE.Vector3(0, 1, 0)
        : new THREE.Vector3(1, 0, 0);
    const right = new THREE.Vector3().crossVectors(dir, worldUp).normalize();
    const up = new THREE.Vector3().crossVectors(right, dir).normalize();

    return Array.from({ length: 28 }, (_, i) => {
      const angle = (i / 28) * Math.PI * 2;
      const tier = i % 4;
      const spreadBase = 0.045 + tier * 0.032;

      const pts: THREE.Vector3[] = [];
      for (let j = 0; j <= 10; j++) {
        const t = j / 10;
        const taper = spreadBase * (1 - t * 0.62);
        const base = origin.clone().multiplyScalar(0.26 + t * 0.69);
        const or = right.clone().multiplyScalar(Math.cos(angle + t * 1.2) * taper);
        const ou = up.clone().multiplyScalar(Math.sin(angle + t * 1.2) * taper);
        const wave = dir.clone().multiplyScalar(0.018 * Math.sin(t * Math.PI * 4 + angle));
        pts.push(base.add(or).add(ou).add(wave));
      }
      return new THREE.CatmullRomCurve3(pts);
    });
  }, [origin]);

  useFrame(({ clock }) => {
    matsRef.current.forEach((mat, i) => {
      if (mat) {
        const ph = i * 0.38 + clock.elapsedTime * 2.8;
        mat.emissiveIntensity = 1.6 + 1.7 * Math.abs(Math.sin(ph));
      }
    });
  });

  if (!visible || tubes.length === 0) return null;

  return (
    <group>
      {tubes.map((curve, i) => (
        <mesh key={i}>
          <tubeGeometry args={[curve, 32, 0.005 + (i % 4) * 0.002, 6, false]} />
          <meshStandardMaterial
            ref={(el) => { matsRef.current[i] = el; }}
            color="#FFC830"
            emissive="#FF7C00"
            emissiveIntensity={1.6}
            metalness={0.1}
            roughness={0.04}
          />
        </mesh>
      ))}
    </group>
  );
}

// ─── Ambient dust particles ───────────────────────────────────────────────────

function Particles() {
  const ref = useRef<THREE.Points>(null!);
  const COUNT = 200;

  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    const pos = new Float32Array(COUNT * 3);
    for (let i = 0; i < COUNT; i++) {
      const r = 2.8 + Math.random() * 4.5;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
    }
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    return g;
  }, []);

  useFrame(({ clock }) => {
    if (ref.current) ref.current.rotation.y = clock.elapsedTime * 0.014;
  });

  return (
    <points ref={ref} geometry={geo}>
      <pointsMaterial
        color="#3858A8"
        size={0.014}
        sizeAttenuation
        transparent
        opacity={0.55}
      />
    </points>
  );
}

// ─── Camera rig with GSAP ─────────────────────────────────────────────────────

const CAM_INIT = new THREE.Vector3(0, 0, 5);

function CameraRig({
  targetNode,
  isZoomed,
  onZoomIn,
  onZoomOut,
}: {
  targetNode: THREE.Vector3 | null;
  isZoomed: boolean;
  onZoomIn: () => void;
  onZoomOut: () => void;
}) {
  const { camera } = useThree();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const ctrlRef = useRef<any>(null);
  const tlRef = useRef<gsap.core.Timeline | null>(null);

  // Zoom IN
  useEffect(() => {
    if (!isZoomed || !targetNode || !ctrlRef.current) return;

    tlRef.current?.kill();
    ctrlRef.current.enabled = false;

    const dest = targetNode.clone().multiplyScalar(0.52);
    const look = targetNode.clone().multiplyScalar(1.06);

    const cp = { x: camera.position.x, y: camera.position.y, z: camera.position.z };
    const lp = {
      x: ctrlRef.current.target.x,
      y: ctrlRef.current.target.y,
      z: ctrlRef.current.target.z,
    };

    tlRef.current = gsap.timeline({ onComplete: onZoomIn });
    tlRef.current
      .to(cp, {
        x: dest.x, y: dest.y, z: dest.z,
        duration: 3.4,
        ease: 'power3.inOut',
        onUpdate() {
          camera.position.set(cp.x, cp.y, cp.z);
          ctrlRef.current.target.set(lp.x, lp.y, lp.z);
          ctrlRef.current.update();
        },
      })
      .to(lp, { x: look.x, y: look.y, z: look.z, duration: 3.4, ease: 'power3.inOut' }, '<');

    return () => { tlRef.current?.kill(); };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isZoomed, targetNode]);

  // Zoom OUT
  useEffect(() => {
    if (isZoomed || !ctrlRef.current) return;
    if (camera.position.distanceTo(CAM_INIT) < 0.05) return;

    tlRef.current?.kill();
    ctrlRef.current.enabled = false;

    const cp = { x: camera.position.x, y: camera.position.y, z: camera.position.z };
    const lp = {
      x: ctrlRef.current.target.x,
      y: ctrlRef.current.target.y,
      z: ctrlRef.current.target.z,
    };

    tlRef.current = gsap.timeline({
      onComplete: () => {
        ctrlRef.current.enabled = true;
        onZoomOut();
      },
    });
    tlRef.current
      .to(cp, {
        x: CAM_INIT.x, y: CAM_INIT.y, z: CAM_INIT.z,
        duration: 2.8,
        ease: 'power2.inOut',
        onUpdate() {
          camera.position.set(cp.x, cp.y, cp.z);
          ctrlRef.current.target.set(lp.x, lp.y, lp.z);
          ctrlRef.current.update();
        },
      })
      .to(lp, { x: 0, y: 0, z: 0, duration: 2.8, ease: 'power2.inOut' }, '<');

    return () => { tlRef.current?.kill(); };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isZoomed]);

  return (
    <OrbitControls
      ref={ctrlRef}
      enablePan={false}
      enableZoom={false}
      autoRotate={!isZoomed}
      autoRotateSpeed={0.35}
      minPolarAngle={Math.PI * 0.2}
      maxPolarAngle={Math.PI * 0.8}
    />
  );
}

// ─── Scene root ───────────────────────────────────────────────────────────────

export default function BrainScene({
  isZoomed,
  setIsZoomed,
}: {
  isZoomed: boolean;
  setIsZoomed: (v: boolean) => void;
}) {
  const [target, setTarget] = useState<THREE.Vector3 | null>(null);
  const [fibersOn, setFibersOn] = useState(false);

  const geo = useMemo(() => buildBrainGeometry(), []);
  const synapses = useMemo(() => pickSynapses(geo, 32), [geo]);

  const handleClick = useCallback(() => {
    if (isZoomed) return;
    setTarget(synapses[0].clone());
    setIsZoomed(true);
  }, [isZoomed, synapses, setIsZoomed]);

  const handleZoomIn = useCallback(() => setFibersOn(true), []);
  const handleZoomOut = useCallback(() => {
    setFibersOn(false);
    setTarget(null);
  }, []);

  return (
    <>
      <ambientLight intensity={0.04} />
      <pointLight position={[4, 5, 3]} intensity={1.4} color="#2848D0" />
      <pointLight position={[-4, -3, -2]} intensity={0.7} color="#0818A0" />
      <pointLight position={[0, 0, 4]} intensity={0.35} color="#7080B0" />

      <Particles />
      <BrainWireframe geo={geo} />

      {synapses.map((pos, i) => (
        <SynapseNode
          key={`${(pos.x * 100) | 0},${(pos.y * 100) | 0}`}
          position={pos}
          prominent={i === 0}
          onClick={i === 0 ? handleClick : undefined}
        />
      ))}

      <FiberOpticPaths origin={target} visible={fibersOn} />

      <CameraRig
        targetNode={target}
        isZoomed={isZoomed}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
      />

      <EffectComposer>
        <Bloom
          luminanceThreshold={0.1}
          luminanceSmoothing={0.9}
          intensity={2.4}
          mipmapBlur
          radius={0.85}
        />
      </EffectComposer>
    </>
  );
}
