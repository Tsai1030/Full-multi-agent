import Image from "next/image";
import StarField from "./StarField";

interface CosmicBackgroundProps {
  dimOverlay?: boolean; // true = slightly dimmer (for form pages)
}

export default function CosmicBackground({ dimOverlay = false }: CosmicBackgroundProps) {
  return (
    <>
      {/* Base image */}
      <div className="fixed inset-0 z-0">
        <Image
          src="/background.png"
          alt=""
          fill
          priority
          className="object-cover object-center"
          quality={90}
        />
        {/* Dark vignette overlay */}
        <div
          className="absolute inset-0"
          style={{
            background: dimOverlay
              ? "rgba(4,2,15,0.70)"
              : "rgba(4,2,15,0.55)",
          }}
        />
        {/* Radial fade to deep at edges */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(ellipse 80% 70% at 50% 50%, transparent 0%, rgba(4,2,15,0.6) 100%)",
          }}
        />
      </div>

      {/* Particle stars */}
      <StarField />

      {/* Ambient purple nebula glow */}
      <div
        className="fixed pointer-events-none z-[2]"
        style={{
          top: "20%",
          left: "10%",
          width: "40vw",
          height: "40vw",
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(123,63,190,0.08) 0%, transparent 70%)",
          filter: "blur(40px)",
        }}
        aria-hidden
      />
      <div
        className="fixed pointer-events-none z-[2]"
        style={{
          bottom: "10%",
          right: "5%",
          width: "30vw",
          height: "30vw",
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(201,168,76,0.06) 0%, transparent 70%)",
          filter: "blur(50px)",
        }}
        aria-hidden
      />
    </>
  );
}
