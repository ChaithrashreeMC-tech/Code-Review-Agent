// TC-010: React Rendering Efficiency (PERF11 violation)
// Expected: PERF11 finding for large unvirtualized list; false-positive cases should NOT trigger
// Technology: React / TypeScript

import React, { useState, useMemo, useEffect } from "react";

interface Product {
  id: number;
  name: string;
  price: number;
  category: string;
}

// ============================================================
// VIOLATION 1: Large list rendered without virtualization
// ============================================================

interface ProductListViolationProps {
  products: Product[]; // Can be 50,000 items from the catalog API
}

export const ProductListViolation: React.FC<ProductListViolationProps> = ({
  products,
}) => {
  /**
   * VIOLATION: Maps over up to 50,000 products and renders a DOM node per item.
   * With 50,000 items the browser creates 50,000+ DOM nodes, causing:
   * - Initial render time of several seconds
   * - UI thread freeze on scroll
   * - High memory usage
   */
  return (
    <ul>
      {products.map((p) => (
        <li key={p.id}>
          {p.name} — ${p.price}
        </li>
      ))}
    </ul>
  );
};


// ============================================================
// VIOLATION 2: Inline object literal causing unnecessary re-renders
// ============================================================

interface FilterPanelProps {
  onFilterChange: (filters: { category: string; minPrice: number }) => void;
}

export const FilterPanelViolation: React.FC<FilterPanelProps> = ({
  onFilterChange,
}) => {
  const [category, setCategory] = useState("all");

  useEffect(() => {
    /**
     * VIOLATION: { category, minPrice: 0 } creates a new object reference
     * on every render, so this effect fires on every re-render regardless
     * of whether category actually changed.
     */
    onFilterChange({ category, minPrice: 0 }); // VIOLATION: new object each render
  }, [{ category, minPrice: 0 }, onFilterChange]); // VIOLATION: new array each render

  return (
    <select value={category} onChange={(e) => setCategory(e.target.value)}>
      <option value="all">All</option>
      <option value="electronics">Electronics</option>
    </select>
  );
};


// ============================================================
// VIOLATION 3: Expensive computation in render body without memoization
// ============================================================

export const ProductStatisticsViolation: React.FC<{ products: Product[] }> = ({
  products,
}) => {
  /**
   * VIOLATION: This sort + filter + reduce runs on every render, even when
   * `products` has not changed. In a parent that re-renders frequently
   * (e.g., due to unrelated state), this computation runs unnecessarily.
   */
  const stats = products  // VIOLATION: no useMemo
    .filter((p) => p.price > 0)
    .sort((a, b) => b.price - a.price)
    .reduce(
      (acc, p) => ({
        total: acc.total + p.price,
        count: acc.count + 1,
        highest: Math.max(acc.highest, p.price),
      }),
      { total: 0, count: 0, highest: 0 }
    );

  return (
    <div>
      <p>Total: ${stats.total}</p>
      <p>Count: {stats.count}</p>
      <p>Highest: ${stats.highest}</p>
    </div>
  );
};


// ============================================================
// SAFE IMPLEMENTATIONS
// ============================================================

import { FixedSizeList as List } from "react-window";

// SAFE 1: Virtualized list — renders only visible rows
export const ProductListSafe: React.FC<ProductListViolationProps> = ({
  products,
}) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      {products[index].name} — ${products[index].price}
    </div>
  );

  return (
    <List height={600} itemCount={products.length} itemSize={40} width="100%">
      {Row}
    </List>
  );
};

// SAFE 2: Stable filter object with useMemo
export const FilterPanelSafe: React.FC<FilterPanelProps> = ({ onFilterChange }) => {
  const [category, setCategory] = useState("all");

  const filters = useMemo(
    () => ({ category, minPrice: 0 }),
    [category] // stable reference — only changes when category changes
  );

  useEffect(() => {
    onFilterChange(filters);
  }, [filters, onFilterChange]);

  return (
    <select value={category} onChange={(e) => setCategory(e.target.value)}>
      <option value="all">All</option>
      <option value="electronics">Electronics</option>
    </select>
  );
};

// SAFE 3: Memoized expensive computation
export const ProductStatisticsSafe: React.FC<{ products: Product[] }> = ({
  products,
}) => {
  const stats = useMemo(
    () =>
      products
        .filter((p) => p.price > 0)
        .sort((a, b) => b.price - a.price)
        .reduce(
          (acc, p) => ({
            total: acc.total + p.price,
            count: acc.count + 1,
            highest: Math.max(acc.highest, p.price),
          }),
          { total: 0, count: 0, highest: 0 }
        ),
    [products] // recomputes only when products changes
  );

  return (
    <div>
      <p>Total: ${stats.total}</p>
      <p>Count: {stats.count}</p>
      <p>Highest: ${stats.highest}</p>
    </div>
  );
};


// ============================================================
// NOT APPLICABLE: Small static list — no virtualization needed
// ============================================================

const NAV_ITEMS = [
  { id: 1, label: "Home" },
  { id: 2, label: "Products" },
  { id: 3, label: "About" },
];

export const NavigationMenu: React.FC = () => {
  /**
   * NOT APPLICABLE: Only 3 items, hardcoded. No virtualization needed.
   * PERF11 must not be flagged for this component.
   */
  return (
    <nav>
      <ul>
        {NAV_ITEMS.map((item) => (
          <li key={item.id}>{item.label}</li>
        ))}
      </ul>
    </nav>
  );
};

