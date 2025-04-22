export type QuestionType = "radio" | "select" | "slider" | "input" | "checkbox" | "range"

export interface Question {
  id: string
  category: string
  title: string
  type: QuestionType
  options?: string[]
  min?: number
  max?: number
  unit?: string
  multi?: boolean
  icon?: string
  rangeIds?: [string]
}