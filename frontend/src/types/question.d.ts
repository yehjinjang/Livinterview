export type QuestionType =
  | "radio"
  | "select"
  | "slider"
  | "input"
  | "checkbox"
  | "range"
  | "autocomplete";

export interface Question {
  id: string;
  main_category: string;
  sub_category: string;
  content: string;
  input_type: QuestionType;
  answers?: string[];
  code?: number;
  multi?: boolean;
  icon_path?: string;
  rangeIds?: [string];
}
