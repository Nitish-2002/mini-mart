// The session cookie is httpOnly (CR-004) — JS can't read it to tell "never
// logged in" apart from "had a session that lapsed" when a 401 comes back,
// but ds-auth-011 (experience-design.md §4C) only wants the interrupt
// banner for the latter. This is the one non-secret signal that lets a
// protected page's 401 handler tell the two apart.
const KEY = "minimart-had-session";

export function markSessionActive(): void {
  try {
    localStorage.setItem(KEY, "1");
  } catch {
    // Storage can throw (private browsing, disabled storage) — the worst
    // case is falling back to a silent redirect instead of the interrupt
    // banner, never a broken page.
  }
}

export function hadSession(): boolean {
  try {
    return localStorage.getItem(KEY) === "1";
  } catch {
    return false;
  }
}
