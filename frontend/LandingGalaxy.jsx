import Galaxy from './Galaxy';

const LandingGalaxy = () => {
  return (
    <div className="galaxy-layer">
      <Galaxy
        mouseRepulsion={true}
        mouseInteraction={true}
        density={1.35}
        glowIntensity={0.3}
        saturation={0.0}
        hueShift={140}
        speed={1.15}
        starSpeed={0.7}
        twinkleIntensity={0.3}
        rotationSpeed={0.08}
        repulsionStrength={2.8}
        transparent={true}
      />
    </div>
  );
};

export default LandingGalaxy;
