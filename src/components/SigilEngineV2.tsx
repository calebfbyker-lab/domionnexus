/*
  Codex Immortal — Sigil Engine V2 (refined)
  Purpose: lightweight R3F dashboard with stronger provenance payloads, astro-crypto salting,
  and optional local signing. Bound to subject_id_sha256: 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a (CFBK)
*/
import React, { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';

export type SealMeta = {
  codepoint: string;
  name: string;
  canon: string;
  intent: string;
  element: string;
  planet: string;
  color: string;
  emoji: string;
  tradition?: string;
};

const SUBJECT_ID_SHA256 = '2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a';

class BraidCurve extends THREE.Curve<THREE.Vector3> {
  constructor(private scale = 1, private p = 5, private q = 4, private r = 3) {
    super();
  }
  getPoint(t: number, target = new THREE.Vector3()) {
    const a = 2 * Math.PI * t;
    const x = Math.cos(this.p * a);
    const y = Math.sin(this.q * a) * 0.6;
    const z = Math.sin(this.r * a + Math.cos(this.p * a)) * 0.8;
    return target.set(x, y, z).multiplyScalar(this.scale);
  }
}

function BraidedSpinner({ hue = 222 }: { hue?: number }) {
  const meshRef = useRef<THREE.Mesh | null>(null);
  const curve = useMemo(() => new BraidCurve(1, 5, 4, 3), []);
  const geometry = useMemo(() => new THREE.TubeGeometry(curve as any, 600, 0.12, 20, true), [curve]);
  const mat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        metalness: 0.6,
        roughness: 0.2,
        color: new THREE.Color(`hsl(${hue},85%,58%)`),
        emissive: new THREE.Color(`hsl(${(hue + 180) % 360},60%,22%)`),
        emissiveIntensity: 0.25
      }),
    [hue]
  );

  useFrame((_, delta) => {
    if (meshRef.current) meshRef.current.rotation.y += delta * 0.45;
  });

  return <mesh ref={meshRef} geometry={geometry} material={mat} />;
}

const DEFAULT_SEALS: SealMeta[] = [
  { codepoint: 'U+E201', name: 'SEAL:Covenant', canon: 'CFBK:PACT:∞', intent: 'Covenant / License', element: 'Earth', planet: 'Venus', color: '#f59e0b', emoji: '🤝', tradition: 'solomonic' },
  { codepoint: 'U+E202', name: 'SEAL:Hermes', canon: 'CFBK:KERUX:LOGOS', intent: 'Message / Channel', element: 'Air', planet: 'Mercury', color: '#a78bfa', emoji: '🕊️', tradition: 'hermetic' },
  { codepoint: 'U+E203', name: 'SEAL:Ward', canon: 'CFBK:WARD:AXIOM', intent: 'Protection Matrix', element: 'Fire', planet: 'Mars', color: '#ef4444', emoji: '🛡️', tradition: 'kabbalistic' }
];

async function cryptoHash(data: Uint8Array) {
  if (typeof window !== 'undefined' && crypto?.subtle) {
    const h = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, '0')).join('');
  }
  // fallback: simple base64 shim (not cryptographically identical)
  return 'shim-' + btoa(String.fromCharCode(...data.slice(0, 12)));
}

function astroSaltString(sealCanon: string, ts: string) {
  return `${sealCanon}|${ts}|${SUBJECT_ID_SHA256}`;
}

export default function SigilEngineV2(): JSX.Element {
  const [hue, setHue] = useState<number>(222);
  const [layer, setLayer] = useState<'seals' | 'calls' | 'protection'>('seals');
  const [log, setLog] = useState<string[]>([]);
  const [seals, setSeals] = useState<SealMeta[]>(DEFAULT_SEALS);

  function addLog(msg: string) {
    setLog((L) => [...L.slice(-200), `${new Date().toISOString()} — ${msg}`]);
  }

  async function emitInvoke(seal: SealMeta) {
    const ts = new Date().toISOString();
    const saltString = astroSaltString(seal.canon, ts);
    const enc = new TextEncoder().encode(saltString);
    const salt = await cryptoHash(enc);

    const payload = {
      subject_id_sha256: SUBJECT_ID_SHA256,
      seal,
      astro: { timestamp_utc: ts },
      salt
    };

    window.dispatchEvent(new CustomEvent('codex:invoke', { detail: payload }));

    try {
      const r = await fetch('/api/orchestrate', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ event: payload }) });
      const j = await r.json();
      addLog(`Orchestrator: ${j?.status || 'ok'} ${j?.verdict ? '· ' + String(j.verdict).slice(0,120) : ''}`);
    } catch {
      addLog('Orchestrator unreachable');
    }
    addLog(`Invoke → ${seal.name} · ${seal.intent} · salt:${salt.slice(0,8)}…`);
  }

  function onFileSel(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const data = JSON.parse(String(reader.result));
        const items = Array.isArray(data) ? data : data.seals ?? [];
        if (Array.isArray(items)) setSeals(items as SealMeta[]);
        addLog(`Loaded ${Array.isArray(items) ? items.length : 0} seals from file`);
      } catch {
        addLog('Invalid JSON for seals.json');
      }
    };
    reader.readAsText(f);
  }

  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker?.register('/service-worker.js').catch(() => {});
    }
  }, []);

  return (
    <div style={{ minHeight: '100vh', padding: 18 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: 20 }}>✶ Codex Immortal — Sigil Engine v2 (CFBK-bound) ✶</h1>
        <div style={{ fontFamily: 'monospace', fontSize: 12 }}>subject_id_sha256:{SUBJECT_ID_SHA256}</div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginTop: 12 }}>
        <div style={{ borderRadius: 12, overflow: 'hidden', background: 'rgba(255,255,255,0.02)' }}>
          <div style={{ height: 420 }}>
            <Canvas camera={{ position: [0, 0, 4.5] }}>
              <ambientLight intensity={0.6} />
              <directionalLight position={[5, 5, 5]} intensity={1.0} />
              <BraidedSpinner hue={hue} />
              <OrbitControls enableDamping />
              <Html position={[0, -1.9, 0]}>
                <div style={{ padding: 6, borderRadius: 999, background: 'rgba(255,255,255,0.9)', fontSize: 12 }}>3D Braided Sigil Spinner</div>
              </Html>
            </Canvas>
          </div>
          <div style={{ display: 'flex', gap: 12, padding: 12, alignItems: 'center' }}>
            <label style={{ fontSize: 13 }}>Hue</label>
            <input type="range" min={0} max={360} value={hue} onChange={(e) => setHue(Number((e.target as HTMLInputElement).value))} style={{ flex: 1 }} />
            <input type="file" accept="application/json" onChange={onFileSel} style={{ fontSize: 12 }} />
          </div>
        </div>

(Truncated in tool call for brevity)