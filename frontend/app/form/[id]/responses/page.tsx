"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { FormAnalytics, ResponseSummary, ResponseOut } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download, Users, CheckCircle, AlertCircle } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";

export default function ResponsesPage({ params }: { params: Promise<{ id: string }> }) {
  const [formId, setFormId] = useState<string>("");
  const [responses, setResponses] = useState<ResponseSummary[]>([]);
  const [analytics, setAnalytics] = useState<FormAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    async function fetchData(id: string) {
      setFormId(id);
      try {
        const [resData, analyticsData] = await Promise.all([
          api.getResponses(id),
          api.getAnalytics(id),
        ]);
        setResponses(resData);
        setAnalytics(analyticsData);
      } catch (error) {
        console.error("Error fetching data", error);
      } finally {
        setLoading(false);
      }
    }
    params.then((p) => fetchData(p.id));
  }, [params]);

  const completionRate = responses.length > 0
    ? Math.round((responses.filter(r => r.completion_status === "complete").length / responses.length) * 100)
    : 0;

  const handleExportCSV = async () => {
    if (!analytics || responses.length === 0) return;
    setExporting(true);
    try {
      const headers = ["Response ID", "Submitted At", "Status", ...analytics.questions.map(q => `"${q.question_title}"`)];
      let csvContent = headers.join(",") + "\n";

      for (const summary of responses) {
        const fullResp: ResponseOut = await api.getResponse(summary.id);
        const row = [
          summary.id,
          summary.submitted_at,
          summary.completion_status,
          ...analytics.questions.map(q => {
            const answer = fullResp.answers.find(a => a.question_id === q.question_id);
            const val = answer?.answer_value || "";
            return `"${val.replace(/"/g, '""')}"`;
          })
        ];
        csvContent += row.join(",") + "\n";
      }

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `responses_${formId}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Export failed", e);
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return <div className="flex h-screen items-center justify-center"><p className="text-muted-foreground">Loading responses...</p></div>;
  }

  return (
    <div className="container mx-auto py-8 max-w-5xl">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/"><ArrowLeft size={20} /></Link>
          </Button>
          <h1 className="text-3xl font-bold">Responses & Analytics</h1>
        </div>
        <Button onClick={handleExportCSV} variant="outline" className="gap-2" disabled={exporting || responses.length === 0}>
          <Download size={16} />
          {exporting ? "Exporting..." : "Export CSV"}
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="pt-6 flex items-center gap-4">
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-full">
              <Users size={20} className="text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Responses</p>
              <p className="text-2xl font-bold">{responses.length}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 flex items-center gap-4">
            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-full">
              <CheckCircle size={20} className="text-green-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Completion Rate</p>
              <p className="text-2xl font-bold">{completionRate}%</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 flex items-center gap-4">
            <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-full">
              <AlertCircle size={20} className="text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Partial Responses</p>
              <p className="text-2xl font-bold">{responses.filter(r => r.completion_status === "partial").length}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="responses">
        <TabsList className="mb-8">
          <TabsTrigger value="responses">Responses ({responses.length})</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="responses">
          {responses.length === 0 ? (
            <div className="text-center py-20 border rounded-lg border-dashed">
              <Users size={40} className="mx-auto mb-4 text-muted-foreground opacity-40" />
              <p className="text-muted-foreground">No responses yet. Share your form to start collecting!</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {responses.map((resp, i) => (
                <Card key={resp.id}>
                  <CardHeader className="py-4 flex flex-row items-center justify-between">
                    <div className="flex items-center gap-3">
                      <CardTitle className="text-lg">Response #{responses.length - i}</CardTitle>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        resp.completion_status === "complete"
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                          : "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400"
                      }`}>
                        {resp.completion_status}
                      </span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {format(new Date(resp.submitted_at), "PPpp")}
                    </span>
                  </CardHeader>
                  <CardContent className="py-4 border-t bg-muted/10">
                    <div className="flex items-center gap-2">
                      <div className="h-2 flex-1 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full transition-all"
                          style={{ width: `${analytics ? (resp.answer_count / analytics.questions.length) * 100 : 0}%` }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {resp.answer_count}/{analytics?.questions.length ?? "?"} answers
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="analytics">
          {!analytics || analytics.questions.length === 0 ? (
            <div className="text-center py-20 border rounded-lg border-dashed">
              <p className="text-muted-foreground">Not enough data for analytics.</p>
            </div>
          ) : (
            <div className="grid gap-6">
              {analytics.questions.map((q) => (
                <Card key={q.question_id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-lg">{q.question_title}</CardTitle>
                      <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">{q.question_type.replace("_", " ")}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{q.total_answers} answer{q.total_answers !== 1 ? "s" : ""}</p>
                  </CardHeader>
                  <CardContent>
                    {q.distribution && q.distribution.length > 0 && (
                      <div className="space-y-3">
                        {q.distribution.map((dist) => (
                          <div key={dist.option}>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="font-medium">{dist.option}</span>
                              <span className="text-muted-foreground">{dist.percentage}% ({dist.count})</span>
                            </div>
                            <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                              <div className="h-full bg-primary transition-all duration-500" style={{ width: `${dist.percentage}%` }} />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {q.average !== null && q.average !== undefined && (
                      <div className="flex gap-6 items-center">
                        <div className="bg-primary/10 p-4 rounded-xl text-center">
                          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Average</p>
                          <p className="text-4xl font-bold text-primary">{Number(q.average).toFixed(1)}</p>
                        </div>
                        {q.min_value !== null && q.max_value !== null && (
                          <div className="flex gap-4 text-sm text-muted-foreground">
                            <div>Min: <span className="font-semibold text-foreground">{q.min_value}</span></div>
                            <div>Max: <span className="font-semibold text-foreground">{q.max_value}</span></div>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
