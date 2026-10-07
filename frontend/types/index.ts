export type QuestionType =
  | "short_text"
  | "long_text"
  | "multiple_choice"
  | "dropdown"
  | "email"
  | "number"
  | "yes_no"
  | "rating";

export type FormStatus = "draft" | "published";

export interface QuestionSettings {
  choices?: string[];
  allow_other?: boolean;
  max_rating?: number;
  placeholder?: string;
  min_value?: number;
  max_value?: number;
  [key: string]: any;
}

export interface QuestionBase {
  type: QuestionType;
  title: string;
  description?: string | null;
  required: boolean;
  settings?: QuestionSettings | null;
}

export interface QuestionCreate extends QuestionBase {}

export interface QuestionUpdate {
  title?: string;
  description?: string | null;
  required?: boolean;
  settings?: QuestionSettings | null;
  type?: QuestionType;
}

export interface QuestionOut extends QuestionBase {
  id: string;
  form_id: string;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface FormBase {
  title: string;
  description?: string | null;
}

export interface FormCreate extends FormBase {}

export interface FormUpdate extends FormBase {}

export interface FormOut extends FormBase {
  id: string;
  public_id: string;
  status: FormStatus;
  created_at: string;
  updated_at: string;
  published_at?: string | null;
  question_count: number;
  response_count: number;
}

export interface FormDetail extends FormOut {
  questions: QuestionOut[];
}

export interface FormPublishOut {
  id: string;
  public_id: string;
  status: FormStatus;
  published_at: string | null;
  public_url: string;
}

export interface AnswerSubmit {
  question_id: string;
  answer_value?: string | null;
}

export interface ResponseSubmit {
  answers: AnswerSubmit[];
}

export interface ResponseAnswerOut {
  id: string;
  question_id: string;
  answer_value?: string | null;
  question_title?: string | null;
  question_type?: string | null;
}

export interface ResponseOut {
  id: string;
  form_id: string;
  submitted_at: string;
  completion_status: "complete" | "partial";
  answers: ResponseAnswerOut[];
}

export interface ResponseSummary {
  id: string;
  form_id: string;
  submitted_at: string;
  completion_status: "complete" | "partial";
  answer_count: number;
}

export interface ChoiceDistribution {
  option: string;
  count: number;
  percentage: number;
}

export interface QuestionAnalytics {
  question_id: string;
  question_title: string;
  question_type: string;
  total_answers: number;
  distribution?: ChoiceDistribution[] | null;
  average?: number | null;
  min_value?: number | null;
  max_value?: number | null;
  rating_distribution?: Record<string, number> | null;
}

export interface FormAnalytics {
  form_id: string;
  total_responses: number;
  questions: QuestionAnalytics[];
}
