// Ambient TypeScript declarations for modularity validation test cases

declare module 'react' {
  export interface ReactNode {}
  export interface FC<P = {}> {
    (props: P): any;
  }
  export function useState<T>(initialState: T | (() => T)): [T, (newState: T | ((prevState: T) => T)) => void];
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;
  export function useMemo<T>(factory: () => T, deps: any[]): T;
}

declare module 'express' {
  export interface Request {
    body: any;
    params: any;
    query: any;
  }
  export interface Response {
    status(code: number): Response;
    json(body: any): Response;
    send(body: any): Response;
  }
  export interface Router {
    get(path: string, ...handlers: any[]): void;
    post(path: string, ...handlers: any[]): void;
  }
  export function Router(): Router;
}

