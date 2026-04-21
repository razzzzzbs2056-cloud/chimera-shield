'use client';

import { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import BrainScene from './BrainScene';

interface Props {
  isZoomed: boolean;
  setIsZoomed: (v: boolean) => void;
}

export default function BrainCanvas({ isZoomed, setIsZoomed }: Props) {
  return (
    <Canvas
      className="absolute inset-0 w-full h-full"
      camera={{ position: [0, 0, 5], fov: 55, near: 0.001, far: 200 }}
      gl={{ antialias: true, alpha: false, powerPreference: 'high-performance' }}
      dpr={[1, 1.5]}
    >
      <color attach="background" args={['#03030A']} />
      <Suspense fallback={null}>
        <BrainScene isZoomed={isZoomed} setIsZoomed={setIsZoomed} />
      </Suspense>
    </Canvas>
  );
}
