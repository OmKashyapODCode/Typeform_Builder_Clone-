"use client";

import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";
import { FormDetail, QuestionOut } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronUp, ChevronDown, Upload, X, CheckCircle } from "lucide-react";

interface FormTheme {
  primaryColor: string;
  backgroundColor: string;
  fontFamily: string;
}

export default function PublicForm({ params }: { params: Promise<{ publicId: string }> }) {
  const [form, setForm] = useState<FormDetail | null>(null);
  const [error, setError] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [fileAnswers, setFileAnswers] = useState<Record<string, File>>({});
  const [submitted, setSubmitted] = useState(false);
  const [validationError, setValidationError] = useState("");
  const [theme, setTheme] = useState<FormTheme>({
    primaryColor: "#000000",
    backgroundColor: "#ffffff",
    fontFamily: "Inter",
  });

  // Flattened ordered list after logic jump resolution
  const [orderedQuestions, setOrderedQuestions] = useState<QuestionOut[]>([]);

  useEffect(() => {
    async function fetchForm(publicId: string) {
      try {
        const data = await api.getPublicForm(publicId);
        setForm(data);
        setOrderedQuestions(data.questions);
        // Load theme from localStorage
        const savedTheme = localStorage.getItem(`theme_${data.id}`);
        if (savedTheme) setTheme(JSON.parse(savedTheme));
      } catch (err: any) {
        setError(err.message || "This form is not available.");
      }
    }
    params.then((p) => fetchForm(p.publicId));
  }, [params]);

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="bg-white p-10 rounded-2xl shadow text-center max-w-md">
          <div className="text-5xl mb-4">😕</div>
          <h2 className="text-2xl font-bold mb-2">Form Unavailable</h2>
          <p className="text-gray-500">{error}</p>
        </div>
      </div>
    );
  }

  if (!form) {
    return (
      <div className="flex h-screen items-center justify-center" style={{ backgroundColor: theme.backgroundColor }}>
        <div className="animate-pulse text-gray-400" style={{ fontFamily: theme.fontFamily }}>Loading...</div>
      </div>
    );
  }

  const questions = orderedQuestions;
  if (questions.length === 0) return <div className="p-8 text-center">This form has no questions.</div>;

  const currentQuestion = questions[currentIndex];

  // Logic jump resolution: find next question index after answering current
  const getNextIndex = (answeredQuestion: QuestionOut, answerValue: string): number => {
    const jumpKey = `jump_${answeredQuestion.id}_${answerValue}`;
    const jumpTarget = answeredQuestion.settings?.[jumpKey];
    if (jumpTarget === "end") return questions.length; // go to end
    if (jumpTarget) {
      const targetIdx = questions.findIndex((q) => q.id === jumpTarget);
      if (targetIdx !== -1) return targetIdx;
    }
    return currentIndex + 1;
  };

  const handleNext = (overrideValue?: string) => {
    const value = overrideValue ?? answers[currentQuestion.id] ?? "";
    setValidationError("");

    if (currentQuestion.required && !value && !fileAnswers[currentQuestion.id]) {
      setValidationError("This question requires an answer.");
      return;
    }

    const nextIdx = getNextIndex(currentQuestion, value);

    if (nextIdx >= questions.length) {
      submitForm();
    } else {
      setCurrentIndex(nextIdx);
    }
  };

  const handleChoiceSelect = (choice: string) => {
    setAnswers({ ...answers, [currentQuestion.id]: choice });
    // Auto-advance for choice questions
    setTimeout(() => handleNext(choice), 350);
  };

  const submitForm = async () => {
    try {
      const submitData = {
        answers: [
          ...Object.entries(answers).map(([question_id, answer_value]) => ({
            question_id,
            answer_value: answer_value || null,
          })),
          // File uploads: just store filename as answer value since backend doesn't handle files
          ...Object.entries(fileAnswers).map(([question_id, file]) => ({
            question_id,
            answer_value: file.name,
          })),
        ],
      };
      await api.submitResponse(form!.public_id, submitData);
      setSubmitted(true);
    } catch (err: any) {
      setValidationError(err.message || "Failed to submit. Please try again.");
    }
  };

  if (submitted) {
    return (
      <div
        className="flex h-screen flex-col items-center justify-center text-center px-4"
        style={{ backgroundColor: theme.backgroundColor, fontFamily: theme.fontFamily }}
      >
        <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ type: "spring", stiffness: 200 }}>
          <CheckCircle size={64} className="mx-auto mb-6" style={{ color: theme.primaryColor }} />
          <h1 className="text-4xl font-bold mb-3" style={{ color: theme.primaryColor }}>Thank you!</h1>
          <p className="text-xl text-gray-500">Your response has been submitted successfully.</p>
        </motion.div>
      </div>
    );
  }

  const progress = ((currentIndex) / questions.length) * 100;

  return (
    <div
      className="flex h-screen flex-col overflow-hidden text-gray-900"
      style={{ backgroundColor: theme.backgroundColor, fontFamily: theme.fontFamily, color: "#111827" }}
    >
      {/* Progress bar */}
      <div className="h-1 w-full bg-black/10">
        <motion.div
          className="h-full transition-all"
          style={{ width: `${progress}%`, backgroundColor: theme.primaryColor }}
          animate={{ width: `${progress}%` }}
        />
      </div>

      {/* Question area */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 md:px-20 max-w-3xl mx-auto w-full">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -30, opacity: 0 }}
            transition={{ duration: 0.35, ease: "easeOut" }}
            className="w-full"
          >
            {/* Question header */}
            <div className="mb-8">
              <div className="flex items-start gap-3 mb-2">
                <span className="text-sm font-bold mt-1.5" style={{ color: theme.primaryColor }}>
                  {currentIndex + 1} →
                </span>
                <div>
                  <h2 className="text-2xl md:text-3xl font-semibold leading-snug" style={{ color: "#1a1a1a" }}>
                    {currentQuestion.title}
                    {currentQuestion.required && <span className="text-red-500 ml-1">*</span>}
                  </h2>
                  {currentQuestion.description && (
                    <p className="text-lg text-gray-500 mt-1">{currentQuestion.description}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Question input */}
            <div className="ml-8 mb-6">
              <QuestionInput
                question={currentQuestion}
                value={answers[currentQuestion.id] || ""}
                fileValue={fileAnswers[currentQuestion.id] || null}
                onChange={(val) => {
                  setValidationError("");
                  setAnswers({ ...answers, [currentQuestion.id]: val });
                }}
                onFileChange={(file) => {
                  setValidationError("");
                  setFileAnswers({ ...fileAnswers, [currentQuestion.id]: file });
                }}
                onChoiceSelect={handleChoiceSelect}
                onEnter={handleNext}
                primaryColor={theme.primaryColor}
              />
            </div>

            {/* Validation error */}
            {validationError && (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="ml-8 text-red-500 text-sm mb-4"
              >
                ⚠ {validationError}
              </motion.p>
            )}

            {/* OK button */}
            {!["multiple_choice", "dropdown", "yes_no"].includes(currentQuestion.type) && (
              <div className="ml-8 flex items-center gap-4">
                <button
                  onClick={() => handleNext()}
                  className="px-8 py-2.5 rounded-md text-white font-bold text-base transition-opacity hover:opacity-90 active:scale-95"
                  style={{ backgroundColor: theme.primaryColor }}
                >
                  {currentIndex === questions.length - 1 ? "Submit" : "OK ✓"}
                </button>
                <span className="text-xs text-gray-400">press <strong>Enter ↵</strong></span>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation arrows */}
      <div className="p-4 flex justify-between items-center text-sm text-gray-400">
        <span className="text-xs">{currentIndex + 1} / {questions.length}</span>
        <div className="flex gap-1">
          <button
            onClick={() => { setValidationError(""); setCurrentIndex(Math.max(0, currentIndex - 1)); }}
            disabled={currentIndex === 0}
            className="p-2 rounded hover:bg-black/5 disabled:opacity-30 transition-opacity"
          >
            <ChevronUp size={16} />
          </button>
          <button
            onClick={() => handleNext()}
            disabled={currentIndex >= questions.length - 1}
            className="p-2 rounded hover:bg-black/5 disabled:opacity-30 transition-opacity"
          >
            <ChevronDown size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

function QuestionInput({
  question, value, fileValue, onChange, onFileChange, onChoiceSelect, onEnter, primaryColor
}: {
  question: QuestionOut;
  value: string;
  fileValue: File | null;
  onChange: (v: string) => void;
  onFileChange: (f: File) => void;
  onChoiceSelect: (v: string) => void;
  onEnter: () => void;
  primaryColor: string;
}) {
  const fileRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && question.type !== "long_text") {
      e.preventDefault();
      onEnter();
    }
  };

  switch (question.type) {
    case "short_text":
    case "email":
    case "number":
      return (
        <input
          type={question.type === "number" ? "number" : question.type === "email" ? "email" : "text"}
          className="w-full text-xl bg-transparent border-0 border-b-2 border-gray-200 pb-2 focus:outline-none focus:border-black placeholder-gray-300 transition-colors"
          style={{ borderBottomColor: value ? primaryColor : undefined }}
          placeholder="Type your answer here..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          autoFocus
        />
      );

    case "long_text":
      return (
        <textarea
          className="w-full text-lg bg-transparent border-0 border-b-2 border-gray-200 pb-2 min-h-[120px] focus:outline-none resize-none placeholder-gray-300"
          style={{ borderBottomColor: value ? primaryColor : undefined }}
          placeholder="Type your answer here..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          autoFocus
        />
      );

    case "multiple_choice":
    case "dropdown":
      return (
        <div className="flex flex-col gap-3 w-full">
          {(question.settings?.choices || []).map((choice, i) => (
            <button
              key={choice}
              onClick={() => onChoiceSelect(choice)}
              className={`text-left px-4 py-3 rounded-lg border-2 transition-all flex items-center gap-3 ${
                value === choice ? "border-black bg-black/5 font-medium" : "border-gray-200 hover:border-gray-400"
              }`}
              style={value === choice ? { borderColor: primaryColor, backgroundColor: `${primaryColor}10` } : {}}
            >
              <span
                className="w-6 h-6 rounded border text-xs flex items-center justify-center font-mono shrink-0"
                style={value === choice ? { borderColor: primaryColor, color: primaryColor } : { borderColor: "#ccc", color: "#aaa" }}
              >
                {String.fromCharCode(65 + i)}
              </span>
              {choice}
            </button>
          ))}
        </div>
      );

    case "yes_no":
      return (
        <div className="flex gap-4">
          {["Yes", "No"].map((opt) => (
            <button
              key={opt}
              onClick={() => onChoiceSelect(opt)}
              className={`flex-1 text-center py-8 rounded-xl border-2 transition-all text-xl font-bold`}
              style={value === opt
                ? { borderColor: primaryColor, backgroundColor: `${primaryColor}15`, color: primaryColor }
                : { borderColor: "#e5e7eb", color: "#374151" }
              }
            >
              {opt === "Yes" ? "👍 Yes" : "👎 No"}
            </button>
          ))}
        </div>
      );

    case "rating":
      const max = question.settings?.max_rating || 5;
      return (
        <div className="flex flex-wrap gap-3">
          {Array.from({ length: max }).map((_, i) => (
            <button
              key={i}
              onClick={() => { onChange(String(i + 1)); }}
              className={`w-14 h-14 rounded-xl flex items-center justify-center text-xl font-bold transition-all border-2`}
              style={
                value === String(i + 1)
                  ? { borderColor: primaryColor, backgroundColor: primaryColor, color: "#fff" }
                  : { borderColor: "#e5e7eb", color: "#374151" }
              }
            >
              {i + 1}
            </button>
          ))}
        </div>
      );

    case "file_upload" as any:
      return (
        <div>
          <input
            ref={fileRef}
            type="file"
            className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) onFileChange(f); }}
          />
          {fileValue ? (
            <div className="flex items-center gap-3 px-4 py-3 border-2 rounded-lg border-green-500 bg-green-50">
              <CheckCircle size={18} className="text-green-600 shrink-0" />
              <span className="text-sm font-medium text-green-800 flex-1 truncate">{fileValue.name}</span>
              <button onClick={() => fileRef.current && (fileRef.current.value = "") && onFileChange(null as any)}>
                <X size={16} className="text-green-600 hover:text-red-500" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => fileRef.current?.click()}
              className="flex items-center gap-3 px-6 py-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-gray-400 text-gray-500 hover:text-gray-700 transition-colors"
            >
              <Upload size={20} />
              <span>Click to upload a file</span>
            </button>
          )}
        </div>
      );

    default:
      return <div className="text-red-400 text-sm">Unsupported question type: {question.type}</div>;
  }
}
