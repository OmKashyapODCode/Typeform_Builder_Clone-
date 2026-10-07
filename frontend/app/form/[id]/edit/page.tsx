"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { FormDetail, QuestionOut, QuestionType } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ThemeToggle } from "@/components/ThemeToggle";
import {
  ArrowLeft, GripVertical, Plus, Trash2, Settings, ExternalLink,
  Palette, GitBranch, Type, Hash, Mail, Star, CheckSquare, List,
  AlignLeft, ThumbsUp, Upload
} from "lucide-react";
import Link from "next/link";
import {
  DndContext, closestCenter, KeyboardSensor, PointerSensor,
  useSensor, useSensors, DragEndEvent
} from "@dnd-kit/core";
import {
  arrayMove, SortableContext, sortableKeyboardCoordinates,
  verticalListSortingStrategy, useSortable
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

const QUESTION_TYPE_META: { type: QuestionType; label: string; icon: React.ReactNode }[] = [
  { type: "short_text",      label: "Short Text",      icon: <Type size={14} /> },
  { type: "long_text",       label: "Long Text",       icon: <AlignLeft size={14} /> },
  { type: "multiple_choice", label: "Multiple Choice", icon: <CheckSquare size={14} /> },
  { type: "dropdown",        label: "Dropdown",        icon: <List size={14} /> },
  { type: "email",           label: "Email",           icon: <Mail size={14} /> },
  { type: "number",          label: "Number",          icon: <Hash size={14} /> },
  { type: "yes_no",          label: "Yes / No",        icon: <ThumbsUp size={14} /> },
  { type: "rating",          label: "Rating",          icon: <Star size={14} /> },
  { type: "file_upload" as QuestionType, label: "File Upload", icon: <Upload size={14} /> },
];

interface FormTheme {
  primaryColor: string;
  backgroundColor: string;
  fontFamily: string;
}

const DEFAULT_THEME: FormTheme = {
  primaryColor: "#000000",
  backgroundColor: "#ffffff",
  fontFamily: "Inter",
};

export default function FormBuilder({ params }: { params: Promise<{ id: string }> }) {
  const [formId, setFormId] = useState<string>("");
  const [form, setForm] = useState<FormDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedQuestion, setSelectedQuestion] = useState<QuestionOut | null>(null);
  const [rightPanel, setRightPanel] = useState<"settings" | "theme" | "logic">("settings");
  const [theme, setTheme] = useState<FormTheme>(DEFAULT_THEME);

  useEffect(() => {
    params.then((p) => {
      setFormId(p.id);
      fetchForm(p.id);
    });
  }, [params]);

  const fetchForm = async (id: string) => {
    try {
      const data = await api.getForm(id);
      setForm(data);
      if (data.questions.length > 0 && !selectedQuestion) {
        setSelectedQuestion(data.questions[0]);
      }
      // Load theme from localStorage
      const savedTheme = localStorage.getItem(`theme_${id}`);
      if (savedTheme) setTheme(JSON.parse(savedTheme));
    } catch (error) {
      console.error("Error fetching form", error);
    } finally {
      setLoading(false);
    }
  };

  const saveTheme = (t: FormTheme) => {
    setTheme(t);
    localStorage.setItem(`theme_${formId}`, JSON.stringify(t));
  };

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id && form) {
      const oldIndex = form.questions.findIndex((q) => q.id === active.id);
      const newIndex = form.questions.findIndex((q) => q.id === over.id);
      const newQuestions = arrayMove(form.questions, oldIndex, newIndex);
      setForm({ ...form, questions: newQuestions });
      try {
        await api.reorderQuestions(form.id, newQuestions.map((q) => q.id));
      } catch (err) {
        fetchForm(formId);
      }
    }
  };

  const handleAddQuestion = async (type: QuestionType) => {
    if (!form) return;
    const defaultTitles: Partial<Record<QuestionType, string>> = {
      short_text: "Short answer question",
      long_text: "Tell us more",
      multiple_choice: "Choose one",
      dropdown: "Select an option",
      email: "What's your email?",
      number: "Enter a number",
      yes_no: "Yes or No?",
      rating: "Rate your experience",
      file_upload: "Upload a file",
    } as any;

    const newQ = await api.addQuestion(form.id, {
      type,
      title: defaultTitles[type] || "New Question",
      required: false,
    });
    setForm({ ...form, questions: [...form.questions, newQ] });
    setSelectedQuestion(newQ);
    setRightPanel("settings");
  };

  const handleDeleteQuestion = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!form) return;
    await api.deleteQuestion(id);
    const updated = form.questions.filter((q) => q.id !== id);
    setForm({ ...form, questions: updated });
    if (selectedQuestion?.id === id) setSelectedQuestion(updated[0] ?? null);
  };

  const handlePublish = async () => {
    if (!form) return;
    if (form.status === "draft") {
      const pub = await api.publishForm(form.id);
      setForm({ ...form, status: pub.status, public_id: pub.public_id });
    } else {
      const unpub = await api.unpublishForm(form.id);
      setForm({ ...form, status: unpub.status });
    }
  };

  const handleUpdateQuestion = async (updates: Partial<QuestionOut>) => {
    if (!selectedQuestion || !form) return;
    const updated = { ...selectedQuestion, ...updates };
    setSelectedQuestion(updated);
    setForm({ ...form, questions: form.questions.map((q) => (q.id === updated.id ? updated : q)) });
    await api.updateQuestion(updated.id, updates);
  };

  if (loading || !form) {
    return <div className="flex h-screen items-center justify-center text-muted-foreground">Loading builder...</div>;
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-muted/30">
      {/* Header */}
      <header className="h-14 border-b bg-background flex items-center justify-between px-4 shrink-0 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/"><ArrowLeft size={16} /></Link>
          </Button>
          <Input
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            onBlur={(e) => api.updateForm(form.id, { title: e.target.value })}
            className="w-60 border-transparent hover:border-input focus:border-input shadow-none font-semibold"
          />
          <span className={`text-xs px-2 py-0.5 rounded-full ${
            form.status === "published" ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-muted text-muted-foreground"
          }`}>
            {form.status}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          {form.status === "published" && (
            <Button variant="outline" size="sm" asChild>
              <Link href={`/f/${form.public_id}`} target="_blank" className="gap-2">
                <ExternalLink size={14} /> Preview
              </Link>
            </Button>
          )}
          <Button
            variant={form.status === "published" ? "outline" : "default"}
            size="sm"
            onClick={handlePublish}
          >
            {form.status === "published" ? "Unpublish" : "Publish"}
          </Button>
        </div>
      </header>

      {/* 3-Panel Builder Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Question Types */}
        <div className="w-56 bg-background border-r flex flex-col shrink-0">
          <div className="p-3 border-b text-xs font-semibold text-muted-foreground uppercase tracking-wider">Add Question</div>
          <div className="p-2 space-y-0.5 overflow-y-auto flex-1">
            {QUESTION_TYPE_META.map((qt) => (
              <button
                key={qt.type}
                onClick={() => handleAddQuestion(qt.type)}
                className="w-full flex items-center gap-2.5 p-2 rounded-md hover:bg-muted text-sm text-foreground text-left transition-colors group"
              >
                <span className="text-muted-foreground group-hover:text-foreground transition-colors">{qt.icon}</span>
                {qt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Center: Canvas */}
        <div className="flex-1 overflow-y-auto p-8 flex flex-col items-center bg-muted/20">
          <div className="w-full max-w-2xl">
            {form.questions.length === 0 ? (
              <div className="text-center py-24 border-2 border-dashed rounded-xl bg-background text-muted-foreground">
                <Plus size={32} className="mx-auto mb-3 opacity-30" />
                <p>Click a question type on the left to get started.</p>
              </div>
            ) : (
              <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                <SortableContext items={form.questions.map((q) => q.id)} strategy={verticalListSortingStrategy}>
                  <div className="space-y-3">
                    {form.questions.map((q, idx) => (
                      <SortableQuestion
                        key={q.id}
                        question={q}
                        index={idx}
                        allQuestions={form.questions}
                        isSelected={selectedQuestion?.id === q.id}
                        onSelect={() => { setSelectedQuestion(q); setRightPanel("settings"); }}
                        onDelete={(e: React.MouseEvent) => handleDeleteQuestion(q.id, e)}
                      />
                    ))}
                  </div>
                </SortableContext>
              </DndContext>
            )}
          </div>
        </div>

        {/* Right: Tabbed Settings Panel */}
        <div className="w-80 bg-background border-l shrink-0 flex flex-col">
          {/* Panel Tabs */}
          <div className="flex border-b shrink-0">
            {[
              { key: "settings", label: "Settings", icon: <Settings size={14} /> },
              { key: "theme",    label: "Theme",    icon: <Palette size={14} /> },
              { key: "logic",    label: "Logic",    icon: <GitBranch size={14} /> },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setRightPanel(tab.key as any)}
                className={`flex-1 flex items-center justify-center gap-1.5 py-3 text-xs font-medium border-b-2 transition-colors ${
                  rightPanel === tab.key
                    ? "border-primary text-primary"
                    : "border-transparent text-muted-foreground hover:text-foreground"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto">
            {/* ── SETTINGS PANEL ── */}
            {rightPanel === "settings" && (
              selectedQuestion ? (
                <div className="p-4 space-y-5">
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Title</label>
                    <Input
                      value={selectedQuestion.title}
                      onChange={(e) => handleUpdateQuestion({ title: e.target.value })}
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Description</label>
                    <textarea
                      className="w-full text-sm rounded-md border border-input bg-background p-2 min-h-[80px] focus:outline-none focus:ring-1 focus:ring-ring"
                      value={selectedQuestion.description || ""}
                      onChange={(e) => handleUpdateQuestion({ description: e.target.value })}
                      placeholder="Optional helper text..."
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">Required</label>
                    <input
                      type="checkbox"
                      checked={selectedQuestion.required}
                      onChange={(e) => handleUpdateQuestion({ required: e.target.checked })}
                      className="h-4 w-4 accent-primary"
                    />
                  </div>

                  {/* Choice options */}
                  {(selectedQuestion.type === "multiple_choice" || selectedQuestion.type === "dropdown") && (
                    <div className="space-y-1.5 pt-4 border-t">
                      <label className="text-sm font-medium">Options (one per line)</label>
                      <textarea
                        className="w-full text-sm rounded-md border border-input bg-background p-2 min-h-[120px] focus:outline-none focus:ring-1 focus:ring-ring"
                        value={(selectedQuestion.settings?.choices || []).join("\n")}
                        onChange={(e) => {
                          const choices = e.target.value.split("\n");
                          handleUpdateQuestion({ settings: { ...selectedQuestion.settings, choices } });
                        }}
                        placeholder={"Option A\nOption B\nOption C"}
                      />
                    </div>
                  )}

                  {/* Rating max */}
                  {selectedQuestion.type === "rating" && (
                    <div className="space-y-1.5 pt-4 border-t">
                      <label className="text-sm font-medium">Max Rating</label>
                      <Input
                        type="number"
                        min={2}
                        max={10}
                        value={selectedQuestion.settings?.max_rating || 5}
                        onChange={(e) =>
                          handleUpdateQuestion({ settings: { ...selectedQuestion.settings, max_rating: Number(e.target.value) } })
                        }
                      />
                    </div>
                  )}

                  {/* Number range */}
                  {selectedQuestion.type === "number" && (
                    <div className="grid grid-cols-2 gap-3 pt-4 border-t">
                      <div className="space-y-1.5">
                        <label className="text-sm font-medium">Min</label>
                        <Input type="number"
                          value={selectedQuestion.settings?.min_value ?? ""}
                          onChange={(e) => handleUpdateQuestion({ settings: { ...selectedQuestion.settings, min_value: Number(e.target.value) } })}
                        />
                      </div>
                      <div className="space-y-1.5">
                        <label className="text-sm font-medium">Max</label>
                        <Input type="number"
                          value={selectedQuestion.settings?.max_value ?? ""}
                          onChange={(e) => handleUpdateQuestion({ settings: { ...selectedQuestion.settings, max_value: Number(e.target.value) } })}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-8 text-center text-muted-foreground text-sm">
                  <Settings size={32} className="mx-auto mb-3 opacity-20" />
                  Select a question to edit its settings.
                </div>
              )
            )}

            {/* ── THEME PANEL ── */}
            {rightPanel === "theme" && (
              <div className="p-4 space-y-5">
                <p className="text-sm text-muted-foreground">Customize how your public form looks.</p>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Primary Color</label>
                  <div className="flex gap-2 items-center">
                    <input
                      type="color"
                      value={theme.primaryColor}
                      onChange={(e) => saveTheme({ ...theme, primaryColor: e.target.value })}
                      className="h-10 w-16 rounded border border-input cursor-pointer"
                    />
                    <span className="text-sm text-muted-foreground font-mono">{theme.primaryColor}</span>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Background Color</label>
                  <div className="flex gap-2 items-center">
                    <input
                      type="color"
                      value={theme.backgroundColor}
                      onChange={(e) => saveTheme({ ...theme, backgroundColor: e.target.value })}
                      className="h-10 w-16 rounded border border-input cursor-pointer"
                    />
                    <span className="text-sm text-muted-foreground font-mono">{theme.backgroundColor}</span>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Font</label>
                  <select
                    className="w-full text-sm rounded-md border border-input bg-background p-2 focus:outline-none focus:ring-1 focus:ring-ring"
                    value={theme.fontFamily}
                    onChange={(e) => saveTheme({ ...theme, fontFamily: e.target.value })}
                  >
                    {["Inter", "Roboto", "Georgia", "Courier New", "Arial"].map((f) => (
                      <option key={f} value={f} style={{ fontFamily: f }}>{f}</option>
                    ))}
                  </select>
                </div>
                <div className="pt-4 border-t">
                  <p className="text-xs font-medium mb-2 text-muted-foreground">Preview</p>
                  <div className="rounded-lg p-4 border" style={{ backgroundColor: theme.backgroundColor, fontFamily: theme.fontFamily }}>
                    <div className="text-lg font-bold mb-1" style={{ color: theme.primaryColor }}>Sample Question</div>
                    <div className="text-sm text-gray-500">Your answer here...</div>
                    <button className="mt-3 px-4 py-1.5 rounded text-white text-sm font-medium" style={{ backgroundColor: theme.primaryColor }}>
                      OK →
                    </button>
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={() => saveTheme(DEFAULT_THEME)} className="w-full">
                  Reset to Default
                </Button>
              </div>
            )}

            {/* ── LOGIC PANEL ── */}
            {rightPanel === "logic" && (
              <div className="p-4 space-y-5">
                <p className="text-sm text-muted-foreground">Logic jumps let you skip to a different question based on an answer.</p>
                {!selectedQuestion ? (
                  <div className="text-center text-muted-foreground text-sm py-8">
                    <GitBranch size={32} className="mx-auto mb-3 opacity-20" />
                    Select a question first.
                  </div>
                ) : !["multiple_choice", "yes_no", "dropdown"].includes(selectedQuestion.type) ? (
                  <div className="bg-muted rounded-lg p-4 text-sm text-muted-foreground">
                    Logic jumps are available for <strong>Multiple Choice</strong>, <strong>Dropdown</strong>, and <strong>Yes/No</strong> questions.
                  </div>
                ) : (
                  <div className="space-y-4">
                    <p className="text-sm font-medium">If answer is…</p>
                    {(selectedQuestion.type === "yes_no"
                      ? ["Yes", "No"]
                      : selectedQuestion.settings?.choices || []
                    ).map((choice) => {
                      const jumpKey = `jump_${selectedQuestion.id}_${choice}`;
                      const currentJump = selectedQuestion.settings?.[jumpKey] || "";
                      return (
                        <div key={choice} className="space-y-1.5 p-3 border rounded-lg bg-muted/30">
                          <label className="text-sm font-semibold">"{choice}"</label>
                          <div className="flex gap-2 items-center">
                            <span className="text-sm text-muted-foreground">→ Jump to</span>
                            <select
                              className="flex-1 text-sm rounded-md border border-input bg-background p-1.5 focus:outline-none focus:ring-1 focus:ring-ring"
                              value={currentJump}
                              onChange={(e) => {
                                handleUpdateQuestion({
                                  settings: {
                                    ...selectedQuestion.settings,
                                    [jumpKey]: e.target.value,
                                  }
                                });
                              }}
                            >
                              <option value="">Next question (default)</option>
                              <option value="end">End of form</option>
                              {form.questions
                                .filter((q) => q.id !== selectedQuestion.id)
                                .map((q, idx) => (
                                  <option key={q.id} value={q.id}>
                                    Q{idx + 1}: {q.title.slice(0, 30)}{q.title.length > 30 ? "…" : ""}
                                  </option>
                                ))}
                            </select>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SortableQuestion({ question, index, isSelected, onSelect, onDelete, allQuestions }: any) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: question.id });
  const style = { transform: CSS.Transform.toString(transform), transition };
  const meta = QUESTION_TYPE_META.find((m) => m.type === question.type);

  // Check if this question has any logic jumps
  const hasLogic = question.settings && Object.keys(question.settings).some(k => k.startsWith("jump_"));

  return (
    <div
      ref={setNodeRef}
      style={style}
      onClick={onSelect}
      className={`bg-background rounded-xl shadow-sm border-2 flex items-stretch overflow-hidden group cursor-pointer transition-all hover:shadow-md ${
        isSelected ? "border-primary" : "border-transparent hover:border-border"
      }`}
    >
      <div
        {...attributes}
        {...listeners}
        className="w-8 bg-muted/50 border-r flex items-center justify-center cursor-grab active:cursor-grabbing text-muted-foreground hover:text-foreground"
      >
        <GripVertical size={16} />
      </div>
      <div className="flex-1 p-4">
        <div className="flex justify-between items-start">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-primary">{index + 1}</span>
              <span className="text-xs text-muted-foreground flex items-center gap-1">{meta?.icon} {meta?.label}</span>
              {hasLogic && (
                <span className="text-xs px-1.5 py-0.5 bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 rounded-full flex items-center gap-1">
                  <GitBranch size={10} /> logic
                </span>
              )}
              {question.required && <span className="text-xs text-red-500 font-bold">*</span>}
            </div>
            <div className="font-medium text-foreground truncate">{question.title}</div>
            {question.description && <div className="text-muted-foreground text-sm mt-0.5 truncate">{question.description}</div>}
          </div>
          <button
            onClick={onDelete}
            className="text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity ml-2 shrink-0"
          >
            <Trash2 size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}
