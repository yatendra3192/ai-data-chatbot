import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',  // For static export in production
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '',
  },
  // Rewrites only work in development, not with static export
  // The production build will be served by the backend
};

export default nextConfig;
