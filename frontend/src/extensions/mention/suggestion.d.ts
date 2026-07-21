/**
 * Tiptap Mention 扩展类型声明
 */

import type { SuggestionOptions } from '@tiptap/suggestion'

export interface SuggestionItem {
  label?: string
  id: string | number
}

export const defaultSuggestion: SuggestionOptions
