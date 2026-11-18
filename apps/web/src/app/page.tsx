import { Suspense } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getHealth } from "@/lib/api";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-xl flex-1 flex-col justify-center gap-6 px-4 py-16">
      <div className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight">Filing Thesis Engine</h1>
        <p className="text-muted-foreground">
          Test an AI-infrastructure investment thesis against what companies report to the SEC.
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>System status</CardTitle>
          <CardDescription>Live check of the API and its database connection.</CardDescription>
        </CardHeader>
        <CardContent>
          <Suspense fallback={<StatusRows api="checking" database="checking" />}>
            <LiveStatus />
          </Suspense>
        </CardContent>
      </Card>
    </main>
  );
}

async function LiveStatus() {
  const result = await getHealth();
  if (!result.reachable) {
    return <StatusRows api="unreachable" database="unknown" />;
  }
  return <StatusRows api="ok" database={result.health.database} />;
}

type State = "ok" | "checking" | "unreachable" | "unknown";

function StatusRows({ api, database }: { api: State; database: State }) {
  return (
    <dl className="grid grid-cols-[1fr_auto] items-center gap-y-3 text-sm">
      <dt>API</dt>
      <dd>
        <StatusBadge state={api} />
      </dd>
      <dt>Database</dt>
      <dd>
        <StatusBadge state={database} />
      </dd>
    </dl>
  );
}

function StatusBadge({ state }: { state: State }) {
  const variant = state === "ok" ? "default" : state === "unreachable" ? "destructive" : "outline";
  return <Badge variant={variant}>{state}</Badge>;
}
