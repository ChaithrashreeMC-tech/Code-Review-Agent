// TC-011: Code and Module Delivery (PERF12 violation)
// Expected: PERF12 finding for heavy eager import; false-positive for small utility
// Technology: React / TypeScript / Vite

import React, { lazy, Suspense } from "react";


// ============================================================
// VIOLATION 1: Heavy PDF library imported eagerly in critical path
// ============================================================

/**
 * VIOLATION: pdfjs-dist is ~800 KB gzipped. Importing it at the top level
 * of a module that is loaded on the initial page (e.g. App.tsx) adds ~800 KB
 * to the critical bundle, directly increasing Time-to-Interactive.
 *
 * pdfjs-dist is only needed when the user clicks "View PDF Report" —
 * it should be lazy-loaded.
 */
import * as pdfjsLib from "pdfjs-dist";  // VIOLATION: ~800 KB in critical bundle

export const PdfViewerEager: React.FC<{ url: string }> = ({ url }) => {
  // uses pdfjsLib to render PDF
  return <canvas id="pdf-canvas" />;
};


// ============================================================
// VIOLATION 2: Wildcard import preventing tree-shaking
// ============================================================

/**
 * VIOLATION: `import * as _` prevents the bundler from tree-shaking
 * lodash-es. Even though only `groupBy` is used, the entire library
 * (~24 KB gzipped) may be included depending on the bundler config.
 */
import * as _ from "lodash-es";  // VIOLATION: barrel import

export function groupProductsByCategory(products: { id: number; category: string }[]) {
  return _.groupBy(products, "category");  // only uses groupBy
}


// ============================================================
// VIOLATION 3: No route-level code splitting
// ============================================================

/**
 * VIOLATION: Heavy AnalyticsDashboard component is imported statically
 * and included in the main bundle. It is only shown on /analytics route
 * which is used by < 5% of users, but every user pays the bundle cost.
 */
import AnalyticsDashboard from "./AnalyticsDashboard";  // VIOLATION: no lazy()

export const AppRoutes: React.FC = () => {
  return (
    <div>
      {/* other routes */}
      <AnalyticsDashboard />
    </div>
  );
};


// ============================================================
// SAFE IMPLEMENTATIONS
// ============================================================

// SAFE 1: Lazy-loaded PDF viewer
const PdfViewerLazy = lazy(() => import("./PdfViewer"));  // dynamic import

export const PdfViewerSafe: React.FC<{ url: string; isOpen: boolean }> = ({
  url,
  isOpen,
}) => {
  if (!isOpen) return null;
  return (
    <Suspense fallback={<div>Loading PDF viewer...</div>}>
      <PdfViewerLazy url={url} />
    </Suspense>
  );
};

// SAFE 2: Named import enables tree-shaking
import { groupBy } from "lodash-es";  // SAFE: bundler can tree-shake the rest

export function groupProductsByCategorySafe(
  products: { id: number; category: string }[]
) {
  return groupBy(products, "category");
}

// SAFE 3: Lazy route-level splitting
const AnalyticsDashboardLazy = lazy(() => import("./AnalyticsDashboard"));

export const AppRoutesSafe: React.FC = () => {
  return (
    <div>
      {/* other routes */}
      <Suspense fallback={<div>Loading...</div>}>
        <AnalyticsDashboardLazy />
      </Suspense>
    </div>
  );
};


// ============================================================
// NOT APPLICABLE: Small utility — no lazy loading needed
// ============================================================

/**
 * NOT APPLICABLE: date-fns/format is ~2 KB gzipped when tree-shaken.
 * No lazy loading required. PERF12 must not be flagged here.
 */
import { format } from "date-fns";

export function formatDate(date: Date): string {
  return format(date, "yyyy-MM-dd");
}

