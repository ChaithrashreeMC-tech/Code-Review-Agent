// TC-015: Efficient React Implementation (PERF11 + PERF12 + PERF14 safe)
// Expected: NO findings — this is a deliberately well-implemented React component.
// This case verifies the reviewer does not produce false positives on correct code.
// Technology: React / TypeScript / Redux Toolkit

/**
 * This module demonstrates a correctly implemented React feature covering:
 *   - PERF11: Virtualized large list with proper memoization
 *   - PERF12: Lazy-loaded heavy chart library
 *   - PERF14: Fine-grained Redux selector, debounced search, memoized context
 *
 * The reviewer must NOT flag any of these patterns.
 */

import React, {
  lazy,
  Suspense,
  useState,
  useMemo,
  useCallback,
  createContext,
  useContext,
} from "react";
import { FixedSizeList as List } from "react-window";
import { useSelector } from "react-redux";
import { createSelector } from "@reduxjs/toolkit";
import { useDebounce } from "use-debounce";

interface RootState {
  catalog: {
    products: Array<{ id: number; name: string; price: number; inStock: boolean }>;
  };
}

// ============================================================
// PERF12 SAFE: Chart library loaded only when needed
// ============================================================
const HeavyChartComponent = lazy(() => import("./HeavyChartComponent"));


// ============================================================
// PERF14 SAFE: Fine-grained memoized selector
// ============================================================
const selectInStockProducts = createSelector(
  (state: RootState) => state.catalog.products,
  (products) => products.filter((p) => p.inStock)
  // Stable reference: only recomputes when products array changes
);


// ============================================================
// PERF14 SAFE: Memoized context value
// ============================================================
interface ThemeContextValue {
  theme: "light" | "dark";
  toggleTheme: () => void;
}
const ThemeContext = createContext<ThemeContextValue | null>(null);

export const ThemeProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  // SAFE: useMemo prevents a new object on every render, avoiding cascade re-renders
  const contextValue = useMemo<ThemeContextValue>(
    () => ({
      theme,
      toggleTheme: () => setTheme((t) => (t === "light" ? "dark" : "light")),
    }),
    [theme]
  );

  return (
    <ThemeContext.Provider value={contextValue}>{children}</ThemeContext.Provider>
  );
};


// ============================================================
// PERF11 SAFE: Virtualized list with memoized row
// ============================================================
type Product = { id: number; name: string; price: number; inStock: boolean };

const ProductRow = React.memo<{ product: Product; style: React.CSSProperties }>(
  ({ product, style }) => (
    <div style={style}>
      {product.name} — ${product.price}
    </div>
  )
);
ProductRow.displayName = "ProductRow";

export const InStockProductList: React.FC = () => {
  // Fine-grained selector (PERF14): only re-renders when in-stock list changes
  const inStockProducts = useSelector(selectInStockProducts);

  // Memoized itemData prevents row re-renders when parent re-renders
  const itemData = useMemo(() => inStockProducts, [inStockProducts]);

  const Row = useCallback(
    ({ index, style }: { index: number; style: React.CSSProperties }) => (
      <ProductRow product={itemData[index]} style={style} />
    ),
    [itemData]
  );

  // PERF11 SAFE: react-window renders only visible rows regardless of list size
  return (
    <List
      height={600}
      itemCount={inStockProducts.length}
      itemSize={40}
      width="100%"
    >
      {Row}
    </List>
  );
};


// ============================================================
// PERF14 SAFE: Debounced search with fine-grained local state
// ============================================================
interface ProductSearchProps {
  onSearch: (query: string) => void;
}

export const ProductSearch: React.FC<ProductSearchProps> = ({ onSearch }) => {
  const [query, setQuery] = useState("");
  const [debouncedQuery] = useDebounce(query, 300);

  // API call only fires after 300ms of inactivity
  React.useEffect(() => {
    if (debouncedQuery.length >= 2) {
      onSearch(debouncedQuery);
    }
  }, [debouncedQuery, onSearch]);

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search in-stock products..."
      aria-label="Product search"
    />
  );
};


// ============================================================
// PERF12 SAFE: Main page — chart loaded lazily
// ============================================================
export const ProductDashboard: React.FC = () => {
  const [showChart, setShowChart] = useState(false);

  return (
    <ThemeProvider>
      <div>
        <InStockProductList />
        <ProductSearch onSearch={(q) => console.log("searching:", q)} />

        <button onClick={() => setShowChart(true)}>Show Sales Chart</button>

        {/* HeavyChartComponent is not in the critical bundle */}
        {showChart && (
          <Suspense fallback={<p>Loading chart...</p>}>
            <HeavyChartComponent />
          </Suspense>
        )}
      </div>
    </ThemeProvider>
  );
};

