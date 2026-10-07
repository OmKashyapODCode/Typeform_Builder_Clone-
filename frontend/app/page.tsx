"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { FormOut } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Edit, Copy, Trash2, Eye, BarChart } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function Dashboard() {
  const [forms, setForms] = useState<FormOut[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchForms = async () => {
    try {
      const data = await api.getForms();
      setForms(data);
    } catch (error) {
      console.error("Failed to fetch forms", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForms();
  }, []);

  const handleCreateForm = async () => {
    try {
      const newForm = await api.createForm({ title: "New Form", description: "" });
      router.push(`/form/${newForm.id}/edit`);
    } catch (error) {
      console.error("Failed to create form", error);
    }
  };

  const handleDuplicate = async (id: string) => {
    try {
      await api.duplicateForm(id);
      fetchForms();
    } catch (error) {
      console.error("Failed to duplicate form", error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm("Are you sure you want to delete this form?")) {
      try {
        await api.deleteForm(id);
        fetchForms();
      } catch (error) {
        console.error("Failed to delete form", error);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10 max-w-6xl">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Forms Workspace</h1>
          <p className="text-muted-foreground mt-1">Manage and create your conversational forms.</p>
        </div>
        <div className="flex gap-4 items-center">
          <ThemeToggle />
          <Button onClick={handleCreateForm} className="gap-2">
            <Plus size={16} />
            Create Form
          </Button>
        </div>
      </div>

      {forms.length === 0 ? (
        <div className="text-center py-20 border rounded-lg border-dashed">
          <p className="text-muted-foreground mb-4">You have no forms yet.</p>
          <Button onClick={handleCreateForm} variant="outline" className="gap-2">
            <Plus size={16} />
            Create your first form
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {forms.map((form) => (
            <Card key={form.id} className="flex flex-col">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-xl font-semibold truncate pr-2">
                    {form.title || "Untitled Form"}
                  </CardTitle>
                  <span className={`text-xs px-2 py-1 rounded-full ${form.status === 'published' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {form.status}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground h-10 overflow-hidden">
                  {form.description || "No description provided."}
                </p>
              </CardHeader>
              
              <CardContent className="pb-4 flex-1">
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>{form.question_count} questions</span>
                  <span>{form.response_count} responses</span>
                </div>
              </CardContent>
              
              <CardFooter className="flex justify-between border-t p-4 bg-muted/20">
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" asChild title="Edit Builder">
                    <Link href={`/form/${form.id}/edit`}>
                      <Edit size={16} />
                    </Link>
                  </Button>
                  <Button variant="ghost" size="icon" asChild title="Analytics & Responses">
                    <Link href={`/form/${form.id}/responses`}>
                      <BarChart size={16} />
                    </Link>
                  </Button>
                  {form.status === "published" && (
                    <Button variant="ghost" size="icon" asChild title="View Public Form">
                      <Link href={`/f/${form.public_id}`} target="_blank">
                        <Eye size={16} />
                      </Link>
                    </Button>
                  )}
                </div>
                
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" onClick={() => handleDuplicate(form.id)} title="Duplicate">
                    <Copy size={16} />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => handleDelete(form.id)} className="text-red-500 hover:text-red-600 hover:bg-red-50" title="Delete">
                    <Trash2 size={16} />
                  </Button>
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
