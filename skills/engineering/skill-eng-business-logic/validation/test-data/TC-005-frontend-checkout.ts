// TC-005: Incorrect frontend business behavior & TC-007: Cross-layer tracing
// Spec: specs/checkout/business-spec.md Section 3.1
// Rule: Free shipping applies when cartTotal is >= $50.00. Tax is calculated after shipping exemption.

export function formatCheckoutSummaryViolation(cartTotal: number): { shipping: number; freeShipping: boolean } {
  // VIOLATION (BIZ09 / BIZ05): Frontend uses $75 threshold while backend and spec use $50
  const freeShipping = cartTotal >= 75.0;
  const shipping = freeShipping ? 0.0 : 9.99;
  return { shipping, freeShipping };
}

export function formatCheckoutSummarySafe(cartTotal: number): { shipping: number; freeShipping: boolean } {
  // SAFE: Matches backend and specification threshold of $50
  const freeShipping = cartTotal >= 50.0;
  const shipping = freeShipping ? 0.0 : 9.99;
  return { shipping, freeShipping };
}

