// Server-side only: in Docker the API is reachable at http://api:8000, not localhost.
const API_URL = process.env.API_URL ?? "http://localhost:8000";

// Hand-written until Phase 4, when openapi-typescript generates these from FastAPI's schema.
export type Health = {
  status: "ok" | "error";
  database: "ok" | "unreachable";
};

export type HealthResult = { reachable: true; health: Health } | { reachable: false };

export async function getHealth(): Promise<HealthResult> {
  try {
    const res = await fetch(`${API_URL}/health`, {
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
    // /health answers 503 with a JSON body when the database is down, so read it either way.
    return { reachable: true, health: (await res.json()) as Health };
  } catch {
    return { reachable: false };
  }
}
