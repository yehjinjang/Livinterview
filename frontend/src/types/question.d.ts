export type QuestionType =
  | "radio"
  | "select"
  | "slider"
  | "input"
  | "checkbox"
  | "range"
  | "autocomplete";

export interface Question {
  // id: string;
  main_category: string;
  sub_category: string;
  content: string;
  input_type: QuestionType;
  min?: number;
  max?: number;
  icon_path?: string;
  code?: number;
  answers?: {
    content: string;
    score: number;
  }[];
}
