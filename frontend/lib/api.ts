import {
  FormCreate,
  FormDetail,
  FormOut,
  FormPublishOut,
  FormUpdate,
  QuestionCreate,
  QuestionOut,
  QuestionUpdate,
  ResponseOut,
  ResponseSubmit,
  ResponseSummary,
  FormAnalytics,
} from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = "ApiError";
  }
}

async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });

  if (response.status === 204) {
    return {} as T;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    let message = "An error occurred";
    if (data && data.detail) {
      message = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    }
    throw new ApiError(response.status, message, data);
  }

  return data as T;
}

export const api = {
  // Forms
  getForms: () => fetchAPI<FormOut[]>("/api/forms"),
  getForm: (id: string) => fetchAPI<FormDetail>(`/api/forms/${id}`),
  createForm: (data: FormCreate) => fetchAPI<FormDetail>("/api/forms", { method: "POST", body: JSON.stringify(data) }),
  updateForm: (id: string, data: FormUpdate) => fetchAPI<FormDetail>(`/api/forms/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteForm: (id: string) => fetchAPI<void>(`/api/forms/${id}`, { method: "DELETE" }),
  publishForm: (id: string) => fetchAPI<FormPublishOut>(`/api/forms/${id}/publish`, { method: "POST" }),
  unpublishForm: (id: string) => fetchAPI<FormPublishOut>(`/api/forms/${id}/unpublish`, { method: "POST" }),
  duplicateForm: (id: string) => fetchAPI<FormDetail>(`/api/forms/${id}/duplicate`, { method: "POST" }),

  // Questions
  addQuestion: (formId: string, data: QuestionCreate) => fetchAPI<QuestionOut>(`/api/forms/${formId}/questions`, { method: "POST", body: JSON.stringify(data) }),
  updateQuestion: (questionId: string, data: QuestionUpdate) => fetchAPI<QuestionOut>(`/api/questions/${questionId}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteQuestion: (questionId: string) => fetchAPI<void>(`/api/questions/${questionId}`, { method: "DELETE" }),
  reorderQuestions: (formId: string, questionIds: string[]) => fetchAPI<QuestionOut[]>(`/api/forms/${formId}/questions/reorder`, { method: "PATCH", body: JSON.stringify({ question_ids: questionIds }) }),

  // Public Flow
  getPublicForm: (publicId: string) => fetchAPI<FormDetail>(`/api/public/forms/${publicId}`),
  submitResponse: (publicId: string, data: ResponseSubmit) => fetchAPI<ResponseOut>(`/api/public/forms/${publicId}/responses`, { method: "POST", body: JSON.stringify(data) }),

  // Responses & Analytics
  getResponses: (formId: string) => fetchAPI<ResponseSummary[]>(`/api/forms/${formId}/responses`),
  getResponse: (responseId: string) => fetchAPI<ResponseOut>(`/api/responses/${responseId}`),
  getAnalytics: (formId: string) => fetchAPI<FormAnalytics>(`/api/forms/${formId}/analytics`),
};
