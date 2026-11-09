"use client";

import { useEffect, useRef } from "react";
import {
  animate,
  createAnimatable,
  createScope,
  createTimeline,
  createTimer,
  stagger,
  utils,
} from "animejs";
import styles from "./Hologram.module.css";

type Props = {
  src?: string;
  /** Beam colour as #rrggbb. */
  tint?: string;
  /** Brightness below which the source image is keyed out (0–1). */
  lumaKey?: number;
  /** Strength of glitch bursts (0–1). */
  interference?: number;
  /** Label shown in the HUD corners. */
  label?: string;
  /** CSS aspect-ratio override for the projection bay, e.g. "1 / 1". */
  aspectRatio?: string;
  className?: string;
};

const W = 1280;
const H = 853;

/** Turns the source photo into a tinted, luma-keyed hologram plate with edge glow. */
function buildPlate(img: HTMLImageElement, tint: string, key: number) {
  const raw = document.createElement("canvas");
  raw.width = W;
  raw.height = H;
  const rctx = raw.getContext("2d")!;
  rctx.drawImage(img, 0, 0, W, H);
  const src = rctx.getImageData(0, 0, W, H).data;
  const n = W * H;
  const L = new Float32Array(n);
  for (let i = 0, p = 0; i < n; i++, p += 4) {
    L[i] = (0.2126 * src[p] + 0.7152 * src[p + 1] + 0.0722 * src[p + 2]) / 255;
  }
  const out = new ImageData(W, H);
  const o = out.data;
  const tr = parseInt(tint.slice(1, 3), 16);
  const tg = parseInt(tint.slice(3, 5), 16);
  const tb = parseInt(tint.slice(5, 7), 16);
  for (let y = 1; y < H - 1; y++) {
    for (let x = 1; x < W - 1; x++) {
      const i = y * W + x;
      const gx = L[i - W + 1] + 2 * L[i + 1] + L[i + W + 1] - L[i - W - 1] - 2 * L[i - 1] - L[i + W - 1];
      const gy = L[i + W - 1] + 2 * L[i + W] + L[i + W + 1] - L[i - W - 1] - 2 * L[i - W] - L[i - W + 1];
      const e = Math.min(1, Math.hypot(gx, gy) * 1.6);
      const l = L[i];
      let a = Math.min(1, Math.max(0, (l - key) / 0.35));
      a = a * a * (3 - 2 * a);
      a *= a;
      a = Math.min(1, a * 0.85 + e * 0.6 * (l > key * 0.8 ? 1 : 0));
      const hi = Math.max(0, l - 0.65) * 2.2;
      const b = 0.35 + l * 0.9 + e * 0.4;
      const p = i * 4;
      o[p] = Math.min(255, tr * b + 255 * hi);
      o[p + 1] = Math.min(255, tg * b + 255 * hi);
      o[p + 2] = Math.min(255, tb * b + 255 * hi);
      o[p + 3] = a * 255;
    }
  }
  const plate = document.createElement("canvas");
  plate.width = W;
  plate.height = H;
  plate.getContext("2d")!.putImageData(out, 0, 0);
  return plate;
}

export default function Hologram({
  src = "/hologram/lancehead.jpg",
  tint = "#5fe3ff",
  lumaKey = 0.18,
  interference = 0.3,
  label = "Proj. 01 · Live",
  aspectRatio,
  className,
}: Props) {
  const root = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const bay = root.current;
    const cv = canvas.current;
    if (!bay || !cv) return;
    const ctx = cv.getContext("2d")!;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let scope: ReturnType<typeof createScope> | null = null;
    let cancelled = false;

    // Every visual parameter lives on this object; anime.js tweens it and a timer redraws.
    const fx = { reveal: 0, sweep: 0, burst: 0, flicker: 1, split: 2 };

    const img = new Image();
    img.src = src;
    img.onload = () => {
      if (cancelled) return;
      const plate = buildPlate(img, tint, lumaKey);

      const draw = () => {
        ctx.globalCompositeOperation = "source-over";
        ctx.globalAlpha = 1;
        ctx.clearRect(0, 0, W, H);

        // Materialise from the bottom (emitter side) upwards.
        const top = H * (1 - fx.reveal);
        ctx.save();
        ctx.beginPath();
        ctx.rect(0, top, W, H - top);
        ctx.clip();

        ctx.globalCompositeOperation = "lighter";
        const split = fx.split + fx.burst * 10;
        ctx.globalAlpha = 0.28;
        ctx.drawImage(plate, -split, 0);
        ctx.drawImage(plate, split, 0);
        ctx.globalAlpha = 0.95;
        ctx.drawImage(plate, 0, 0);

        // Interference: displaced horizontal slices while a burst is active.
        const slices = Math.round(fx.burst * (3 + interference * 9));
        for (let s = 0; s < slices; s++) {
          const y = Math.random() * H;
          const h = 3 + Math.random() * 26 * interference;
          const dx = (Math.random() - 0.5) * 90 * interference;
          ctx.globalCompositeOperation = "source-over";
          ctx.clearRect(0, y, W, h);
          ctx.globalCompositeOperation = "lighter";
          ctx.globalAlpha = 0.9;
          ctx.drawImage(plate, 0, y, W, h, dx, y, W, h);
        }

        // Scanlines.
        ctx.globalCompositeOperation = "destination-out";
        ctx.globalAlpha = 0.42;
        ctx.fillStyle = "#000";
        const off = (fx.sweep * 400) % 4;
        for (let y = off; y < H; y += 4) ctx.fillRect(0, y, W, 1.6);

        // Sweep band.
        ctx.globalCompositeOperation = "source-atop";
        const sy = fx.sweep * (H + 240) - 120;
        const g = ctx.createLinearGradient(0, sy - 60, 0, sy + 60);
        g.addColorStop(0, "rgba(255,255,255,0)");
        g.addColorStop(0.5, "rgba(255,255,255,0.35)");
        g.addColorStop(1, "rgba(255,255,255,0)");
        ctx.globalAlpha = 1;
        ctx.fillStyle = g;
        ctx.fillRect(0, sy - 60, W, 120);
        ctx.restore();

        // Bright build line while materialising.
        if (fx.reveal > 0 && fx.reveal < 1) {
          ctx.globalCompositeOperation = "lighter";
          ctx.globalAlpha = 1;
          ctx.fillStyle = tint;
          ctx.fillRect(0, top - 1, W, 3);
          ctx.fillStyle = "rgba(255,255,255,0.8)";
          ctx.fillRect(0, top, W, 1);
        }
        cv.style.opacity = String(fx.flicker);
      };

      if (reduce) {
        fx.reveal = 1;
        fx.sweep = 0.4;
        draw();
        bay.dataset.ready = "true";
        return;
      }

      scope = createScope({ root: bay }).add(() => {
        createTimer({ onUpdate: draw });

        // Intro: emitter powers up, beam opens, ship builds bottom-up, HUD types in.
        createTimeline({ defaults: { ease: "outExpo" } })
          .add(`.${styles.emitter}`, { scale: [0, 1], opacity: [0, 1], duration: 700 })
          .add(`.${styles.cone}`, { scaleY: [0, 1], opacity: [0, 1], duration: 900 }, "-=350")
          .add(fx, { reveal: [0, 1], duration: 1800, ease: "inOutQuad" }, "-=600")
          .add(`.${styles.hudItem}`, { opacity: [0, 1], x: [-12, 0], delay: stagger(110), duration: 500 }, "-=900")
          .add(`.${styles.corner}`, { scale: [1.8, 1], opacity: [0, 0.6], delay: stagger(80), duration: 600 }, "<<");

        // Ambient loops.
        animate(fx, { sweep: [0, 1], duration: 3600, loop: true, ease: "linear" });
        animate(`.${styles.float}`, { y: ["0%", "-1.4%"], duration: 3000, loop: true, alternate: true, ease: "inOutSine" });
        animate(`.${styles.ring}`, {
          scale: [0.6, 1.7],
          opacity: [0.9, 0],
          duration: 2400,
          delay: stagger(800),
          loop: true,
          ease: "outQuad",
        });
        animate(`.${styles.cone}`, { opacity: [0.75, 1], duration: 1600, loop: true, alternate: true, ease: "inOutSine", delay: 2000 });
        animate(fx, {
          flicker: () => utils.random(0.82, 0.96, 2),
          duration: 90,
          loop: true,
          loopDelay: 40,
        });

        // Interference bursts at irregular intervals.
        if (interference > 0) {
          const burst = () => {
            createTimeline({ onComplete: burst })
              .add(fx, { burst: 0, duration: utils.random(1800, 5200) })
              .add(fx, { burst: [0, 1, 0.4, 1, 0], flicker: [1, 0.55, 1], duration: utils.random(160, 420), ease: "linear" });
          };
          burst();
        }

        // Pointer tilt, eased by an animatable.
        const tilt = createAnimatable(cv, { rotateY: 500, rotateX: 500, ease: "outQuad" });
        const yaw = bay.querySelector<HTMLElement>("[data-yaw]");
        const onMove = (e: PointerEvent) => {
          const r = bay.getBoundingClientRect();
          const nx = (e.clientX - r.left) / r.width - 0.5;
          const ny = (e.clientY - r.top) / r.height - 0.5;
          tilt.rotateY(nx * 36);
          tilt.rotateX(-ny * 18);
          if (yaw) yaw.textContent = `Yaw ${(nx * 36).toFixed(1)}° · Pitch ${(-ny * 18).toFixed(1)}°`;
        };
        const onLeave = () => {
          tilt.rotateY(0);
          tilt.rotateX(0);
          if (yaw) yaw.textContent = "Yaw 0.0° · Pitch 0.0°";
        };
        bay.addEventListener("pointermove", onMove);
        bay.addEventListener("pointerleave", onLeave);
        return () => {
          bay.removeEventListener("pointermove", onMove);
          bay.removeEventListener("pointerleave", onLeave);
        };
      });
      bay.dataset.ready = "true";
    };

    return () => {
      cancelled = true;
      scope?.revert();
    };
  }, [src, tint, lumaKey, interference]);

  return (
    <div
      ref={root}
      className={`${styles.bay} ${aspectRatio === "1 / 1" ? styles.square : ""} ${className ?? ""}`}
      style={{ ["--beam" as string]: tint, aspectRatio }}
      role="img"
      aria-label="Hologram projection of a trident-prowed starship"
    >
      <div className={styles.grid} />
      <div className={styles.cone} />
      <div className={styles.emitter}>
        <span className={styles.ring} />
        <span className={styles.ring} />
        <span className={styles.ring} />
      </div>
      <div className={styles.stage}>
        <div className={styles.float}>
          <canvas ref={canvas} className={styles.holo} width={W} height={H} />
        </div>
      </div>
      <span className={`${styles.corner} ${styles.c1}`} />
      <span className={`${styles.corner} ${styles.c2}`} />
      <span className={`${styles.corner} ${styles.c3}`} />
      <span className={`${styles.corner} ${styles.c4}`} />
      <div className={styles.hud} aria-hidden="true">
        <span className={`${styles.hudItem} ${styles.tl}`}>{label}</span>
        <span className={`${styles.hudItem} ${styles.tr}`}>Signal locked</span>
        <span className={`${styles.hudItem} ${styles.bl}`} data-yaw>
          Yaw 0.0° · Pitch 0.0°
        </span>
        <span className={`${styles.hudItem} ${styles.br}`}>Keyed · Luma</span>
      </div>
    </div>
  );
}
