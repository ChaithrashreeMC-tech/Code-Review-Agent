// TC-012: Asset and Network Efficiency (PERF13 violation)
// Expected: PERF13 finding for unoptimized image, missing dimensions, blocking font
// Technology: React / TypeScript / Next.js

import React from "react";
// import Image from "next/image";  // would be SAFE; not imported in violations below


// ============================================================
// VIOLATION 1: Unoptimized image with missing dimensions (CLS risk)
// ============================================================

export const HeroSectionViolation: React.FC = () => {
  /**
   * VIOLATION 1a: Raw <img> with a PNG file. Should use WebP/AVIF format
   * (or Next.js <Image> which handles this automatically).
   *
   * VIOLATION 1b: No width/height specified. The browser reserves no space
   * for the image, causing Cumulative Layout Shift (CLS) when the image loads.
   * CLS > 0.1 fails the Core Web Vitals threshold.
   */
  return (
    <section>
      {/* VIOLATION: unoptimized PNG, no dimensions = CLS */}
      <img
        src="/images/hero-banner.png"
        alt="Hero banner"
        // width and height missing
        // no loading="lazy" (not critical for LCP image, but shows pattern)
      />
      <h1>Welcome to our store</h1>
    </section>
  );
};


// ============================================================
// VIOLATION 2: Render-blocking font without font-display
// ============================================================

/**
 * VIOLATION: The <style> below loads a Google Font synchronously.
 * Without font-display: swap, the browser blocks text rendering until
 * the font is downloaded. On a slow connection this causes FOIT (Flash
 * of Invisible Text).
 *
 * In a real app this would be in a CSS file or <link> in <head>:
 *   @font-face { src: url(...); font-family: 'CustomFont'; }
 *   (missing font-display: swap)
 */
export const FontViolation: React.FC = () => (
  <style>{`
    @font-face {
      font-family: 'BrandFont';
      src: url('/fonts/BrandFont.woff2') format('woff2');
      /* VIOLATION: no font-display: swap */
    }
    body { font-family: 'BrandFont', sans-serif; }
  `}</style>
);


// ============================================================
// VIOLATION 3: Sequential fetch requests that could be parallelized
// (also a false-positive demonstration — they ARE independent)
// ============================================================

export async function loadPageData(productId: string) {
  /**
   * VIOLATION: Three independent fetch calls executed sequentially.
   * Total latency = sum; parallel would be max.
   * (Overlap with PERF01 — report as one root cause, not two findings.)
   */
  const product = await fetch(`/api/products/${productId}`).then((r) => r.json());
  const reviews = await fetch(`/api/products/${productId}/reviews`).then((r) => r.json());
  const related = await fetch(`/api/products/${productId}/related`).then((r) => r.json());
  return { product, reviews, related };
}


// ============================================================
// SAFE IMPLEMENTATIONS
// ============================================================

// SAFE 1: Next.js Image component handles format conversion and dimensions
// (Uncomment next/image import above to use)
// export const HeroSectionSafe: React.FC = () => (
//   <section>
//     <Image
//       src="/images/hero-banner.png"
//       alt="Hero banner"
//       width={1200}
//       height={600}
//       priority  // LCP image — no lazy loading
//     />
//     <h1>Welcome to our store</h1>
//   </section>
// );

// SAFE 1 (plain HTML alternative):
export const HeroSectionSafe: React.FC = () => (
  <section>
    <picture>
      <source srcSet="/images/hero-banner.avif" type="image/avif" />
      <source srcSet="/images/hero-banner.webp" type="image/webp" />
      <img
        src="/images/hero-banner.png"
        alt="Hero banner"
        width={1200}
        height={600}
      />
    </picture>
    <h1>Welcome to our store</h1>
  </section>
);

// SAFE 2: Font with font-display: swap
export const FontSafe: React.FC = () => (
  <style>{`
    @font-face {
      font-family: 'BrandFont';
      src: url('/fonts/BrandFont.woff2') format('woff2');
      font-display: swap;  /* SAFE: shows fallback font immediately */
    }
    body { font-family: 'BrandFont', sans-serif; }
  `}</style>
);

// SAFE 3: Parallel fetches
export async function loadPageDataSafe(productId: string) {
  const [product, reviews, related] = await Promise.all([
    fetch(`/api/products/${productId}`).then((r) => r.json()),
    fetch(`/api/products/${productId}/reviews`).then((r) => r.json()),
    fetch(`/api/products/${productId}/related`).then((r) => r.json()),
  ]);
  return { product, reviews, related };
}


// ============================================================
// NOT APPLICABLE: Small icon — format optimization not required
// ============================================================

export const CloseIcon: React.FC = () => (
  /**
   * NOT APPLICABLE: This is a 16×16 icon (< 1 KB). WebP conversion
   * would save negligible bytes. PERF13 must not be flagged here.
   */
  <img src="/icons/close.svg" alt="Close" width={16} height={16} />
);

