import React from 'react';
import { createRoot } from 'react-dom/client';
import LandingGalaxy from './LandingGalaxy';

const mountNode = document.getElementById('landing-galaxy-root');

if (mountNode) {
  const root = createRoot(mountNode);
  root.render(
    <React.StrictMode>
      <LandingGalaxy />
    </React.StrictMode>
  );
}
