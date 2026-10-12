// Global and module type declarations for React and libraries used in performance test data

declare namespace JSX {
  interface Element extends any {}
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare namespace React {
  export type ReactNode = any;
  export type ReactElement = any;
  export type CSSProperties = Record<string, any>;

  export interface FC<P = {}> {
    (props: P, context?: any): any;
    displayName?: string;
  }

  export type PropsWithChildren<P = {}> = P & { children?: any };

  export interface ChangeEvent<T = any> {
    target: { value: string; [key: string]: any };
  }

  export function useState<T>(initialState: T | (() => T)): [T, (newState: T | ((prevState: T) => T)) => void];
  export function useMemo<T>(factory: () => T, deps?: readonly any[]): T;
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps?: readonly any[]): T;
  export function useEffect(effect: () => void | (() => void), deps?: readonly any[]): void;
  export function createContext<T>(defaultValue: T): {
    Provider: FC<{ value: T; children?: any }>;
    Consumer: FC<{ children: (value: T) => any }>;
  };
  export function useContext<T>(context: any): T;
  export function lazy<T = any>(factory: () => Promise<{ default: T }>): T;
  export const Suspense: FC<{ fallback?: any; children?: any }>;
  export function memo<P = any>(Component: ((props: P) => any) | FC<P>): FC<P>;
}

declare module "react" {
  export = React;
}

declare module "react-window" {
  export const FixedSizeList: React.FC<any>;
}

declare module "react-redux" {
  export function useSelector<TState = any, TSelected = any>(
    selector: (state: TState) => TSelected,
    equalityFn?: (left: TSelected, right: TSelected) => boolean
  ): TSelected;
  export function useDispatch(): (...args: any[]) => any;
}

declare module "@reduxjs/toolkit" {
  export function createSelector(...args: any[]): (...args: any[]) => any;
}

declare module "use-debounce" {
  export function useDebounce<T>(value: T, delay: number, options?: any): [T, { cancel: () => void; flush: () => void; isPending: () => boolean }];
}

declare module "pdfjs-dist" {
  const content: any;
  export default content;
  export const getDocument: any;
}

declare module "lodash-es" {
  export function groupBy<T>(collection: T[], iteratee?: any): Record<string, T[]>;
  const _: any;
  export default _;
}

declare module "date-fns" {
  export function format(date: Date | number, formatStr: string, options?: any): string;
}

declare module "*AnalyticsDashboard" {
  const component: any;
  export default component;
}

declare module "*HeavyChartComponent" {
  const component: any;
  export default component;
}

declare module "*PdfViewer" {
  const component: any;
  export default component;
}
