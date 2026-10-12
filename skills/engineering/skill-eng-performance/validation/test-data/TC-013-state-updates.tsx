// TC-013: State and Update Efficiency (PERF14 violation)
// Expected: PERF14 findings for broad subscription, unstable selector, missing debounce
// Technology: React / TypeScript / Redux Toolkit + Zustand

import React, { useState, useMemo, useCallback } from "react";
import { useSelector, useDispatch } from "react-redux";
import { createSelector } from "@reduxjs/toolkit";
import { useDebounce } from "use-debounce";


// ============================================================
// TYPE DEFINITIONS
// ============================================================

interface RootState {
  catalog: {
    products: Product[];
    filters: { category: string; minPrice: number };
    ui: { isLoading: boolean; selectedProductId: number | null };
    pagination: { page: number; pageSize: number; total: number };
  };
  cart: { items: CartItem[] };
  user: { profile: UserProfile; preferences: UserPreferences };
}

interface Product { id: number; name: string; price: number; category: string }
interface CartItem { productId: number; quantity: number }
interface UserProfile { id: number; name: string; email: string }
interface UserPreferences { theme: string; currency: string }


// ============================================================
// VIOLATION 1: Broad store slice subscription
// ============================================================

export const ProductCountBadgeViolation: React.FC = () => {
  /**
   * VIOLATION: Subscribes to the entire catalog slice.
   * This component only uses catalog.products.length, but it re-renders
   * whenever ANY field in catalog changes — filters, UI, pagination, etc.
   * On a busy catalog page this causes dozens of unnecessary re-renders.
   */
  const catalog = useSelector((state: RootState) => state.catalog);  // VIOLATION

  return <span className="badge">{catalog.products.length}</span>;
};


// ============================================================
// VIOLATION 2: Selector returning new object reference on every call
// ============================================================

export const FilteredProductListViolation: React.FC = () => {
  /**
   * VIOLATION: The selector creates a new array object on every call.
   * Even if the filtered result is identical, React sees a new reference
   * and re-renders the component unnecessarily.
   */
  const filteredProducts = useSelector(
    (state: RootState) =>
      // VIOLATION: new array created each call — defeats memoization
      state.catalog.products.filter((p) => p.price > 100)
  );

  return (
    <ul>
      {filteredProducts.map((p) => (
        <li key={p.id}>{p.name}</li>
      ))}
    </ul>
  );
};


// ============================================================
// VIOLATION 3: setState on every keystroke feeding an API call
// ============================================================

interface SearchBarProps {
  onSearch: (query: string) => void;
}

export const SearchBarViolation: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    /**
     * VIOLATION: onSearch triggers an API call. Called on every keystroke
     * (potentially 10+ times per second during fast typing), this fires
     * 10+ API requests per second, creating unnecessary server load and
     * race-condition risk when responses arrive out of order.
     */
    onSearch(value);  // VIOLATION: no debounce
  };

  return <input value={query} onChange={handleChange} placeholder="Search products..." />;
};


// ============================================================
// SAFE IMPLEMENTATIONS
// ============================================================

// SAFE 1: Specific field selector
export const ProductCountBadgeSafe: React.FC = () => {
  // Only subscribes to the field it actually needs
  const productCount = useSelector(
    (state: RootState) => state.catalog.products.length
  );
  return <span className="badge">{productCount}</span>;
};

// SAFE 2: Memoized selector with createSelector (reselect)
const selectFilteredProducts = createSelector(
  (state: RootState) => state.catalog.products,
  (products) => products.filter((p) => p.price > 100)
  // Result is memoized — same reference returned if products hasn't changed
);

export const FilteredProductListSafe: React.FC = () => {
  const filteredProducts = useSelector(selectFilteredProducts);

  return (
    <ul>
      {filteredProducts.map((p) => (
        <li key={p.id}>{p.name}</li>
      ))}
    </ul>
  );
};

// SAFE 3: Debounced search
export const SearchBarSafe: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState("");
  const [debouncedQuery] = useDebounce(query, 300);  // 300ms debounce

  // API call fires only after 300ms of inactivity
  React.useEffect(() => {
    onSearch(debouncedQuery);
  }, [debouncedQuery, onSearch]);

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search products..."
    />
  );
};


// ============================================================
// NOT APPLICABLE: useMemo not needed for cheap derivation
// ============================================================

export const SimpleGreeting: React.FC<{ name: string }> = ({ name }) => {
  /**
   * NOT APPLICABLE: String concatenation is negligibly cheap.
   * Adding useMemo here would add code complexity for no measurable benefit.
   * PERF14 must not be flagged for this pattern.
   */
  const greeting = `Hello, ${name}!`;  // cheap; no useMemo needed
  return <p>{greeting}</p>;
};

