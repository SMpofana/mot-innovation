import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: __dirname,
  },
  // Use webpack instead of Turbopack to avoid module resolution issues
  // when sharing node_modules with snm_online
  devIndicators: false,
};

export default nextConfig;