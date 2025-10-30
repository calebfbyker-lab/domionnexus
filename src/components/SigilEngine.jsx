import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars } from '@react-three/drei'
import * as THREE from 'three'

function SigilSphere() {
  const meshRef = useRef()
  const particlesRef = useRef()

  // Create sigil geometry
  const sigilGeometry = useMemo(() => {
    const geometry = new THREE.TorusKnotGeometry(1.2, 0.4, 128, 32)
    return geometry
  }, [])

  // Create particle field
  const particles = useMemo(() => {
    const count = 1000
    const positions = new Float32Array(count * 3)
    
    for (let i = 0; i < count; i++) {
      const radius = 3 + Math.random() * 2
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      
      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
      positions[i * 3 + 2] = radius * Math.cos(phi)
    }
    
    return positions
  }, [])

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.2
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3
    }
    
    if (particlesRef.current) {
      particlesRef.current.rotation.y = state.clock.elapsedTime * 0.05
    }
  })

  return (
    <>
      {/* Main Sigil */}
      <mesh ref={meshRef} geometry={sigilGeometry}>
        <meshStandardMaterial
          color="#90e59a"
          emissive="#90e59a"
          emissiveIntensity={0.5}
          wireframe={true}
          transparent={true}
          opacity={0.8}
        />
      </mesh>

      {/* Particle field */}
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particles.length / 3}
            array={particles}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.05}
          color="#7dd088"
          transparent={true}
          opacity={0.6}
          sizeAttenuation={true}
        />
      </points>

      {/* Core light */}
      <pointLight position={[0, 0, 0]} intensity={2} color="#90e59a" />
      
      {/* Ambient light */}
      <ambientLight intensity={0.3} />
    </>
  )
}

function SigilEngine() {
  return (
    <Canvas
      camera={{ position: [0, 0, 6], fov: 60 }}
      style={{ background: '#0b1020' }}
    >
      <Stars
        radius={100}
        depth={50}
        count={5000}
        factor={4}
        saturation={0}
        fade
        speed={1}
      />
      
      <SigilSphere />
      
      <OrbitControls
        enablePan={false}
        enableZoom={true}
        minDistance={3}
        maxDistance={10}
        autoRotate={true}
        autoRotateSpeed={0.5}
      />
    </Canvas>
  )
}

export default SigilEngine
