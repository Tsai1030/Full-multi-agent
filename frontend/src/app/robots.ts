import type { MetadataRoute } from "next";

const BASE_URL = "https://ziwei-frontend.onrender.com";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/account",
          "/profiles",
          "/reading",
          "/master",
          "/career",
          "/love",
          "/pricing",
          "/onboarding",
          "/api/",
        ],
      },
    ],
    sitemap: `${BASE_URL}/sitemap.xml`,
  };
}
