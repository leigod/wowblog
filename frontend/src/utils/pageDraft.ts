/**
 * 页面表单 ↔ 内容编辑器之间的草稿传递
 *
 * 内容编辑器是独立路由（/admin/content-editor），从编辑器返回表单时表单组件会
 * 重新挂载，所以正文和表单里已填好的其它字段需要先“存下来”再“取回来”。
 *
 * 这里把整份草稿放进 sessionStorage，地址栏上只带一个一次性令牌：
 * - 正文不进 URL：长文会让地址长达上百万字符，超出浏览器和服务器的限制；
 * - 只认令牌：正常从列表进入表单（地址上没有令牌）时，不会误套上一次遗留的草稿；
 * - 刷新不丢：令牌留在地址栏里，草稿在 sessionStorage 里，刷新后仍然对得上。
 *
 * sessionStorage 不可用时（如隐私模式限制）退化为仅内存保存：
 * 本次跳转仍然可用，但刷新页面会丢失草稿。
 */

export type PageDraftMode = 'create' | 'edit'

/** 表单里除正文外、打开编辑器之前已经填好的字段 */
export interface PageDraftForm {
  title: string
  slug: string
  image: string
  description: string
}

export interface PageDraft {
  token: string
  mode: PageDraftMode
  /** 编辑模式下的页面 id；新建模式为空字符串 */
  pageId: string
  content: string
  form: PageDraftForm
}

export type PageDraftInput = Omit<PageDraft, 'token'>

/** 地址栏上携带令牌的参数名 */
export const PAGE_DRAFT_QUERY_KEY = 'draft'

const STORAGE_KEY = 'page-content-draft'

let memoryDraft: PageDraft | null = null

const createToken = (): string => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`
}

/** 存储里的内容属于外部数据，使用前先校验结构 */
const isPageDraft = (value: unknown): value is PageDraft => {
  if (!value || typeof value !== 'object') return false
  const draft = value as Record<string, unknown>
  const form = draft.form as Record<string, unknown> | undefined
  return (
    typeof draft.token === 'string' &&
    (draft.mode === 'create' || draft.mode === 'edit') &&
    typeof draft.pageId === 'string' &&
    typeof draft.content === 'string' &&
    !!form &&
    typeof form.title === 'string' &&
    typeof form.slug === 'string' &&
    typeof form.image === 'string' &&
    typeof form.description === 'string'
  )
}

const writeToStorage = (draft: PageDraft | null): void => {
  try {
    if (draft) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(draft))
    } else {
      sessionStorage.removeItem(STORAGE_KEY)
    }
  } catch {
    // 存储不可用或已写满：内存中的副本仍可支撑本次跳转
  }
}

const readFromStorage = (): PageDraft | null => {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed: unknown = JSON.parse(raw)
    return isPageDraft(parsed) ? parsed : null
  } catch {
    return null
  }
}

/** 新建一份草稿并保存，返回带令牌的完整草稿 */
export const createPageDraft = (input: PageDraftInput): PageDraft => {
  const draft: PageDraft = { ...input, token: createToken() }
  savePageDraft(draft)
  return draft
}

export const savePageDraft = (draft: PageDraft): void => {
  memoryDraft = draft
  writeToStorage(draft)
}

/** 按令牌取回草稿；令牌不匹配或草稿不存在时返回 null */
export const getPageDraft = (token?: string | null): PageDraft | null => {
  if (!token) return null
  const draft = memoryDraft ?? readFromStorage()
  return draft && draft.token === token ? draft : null
}

/** 丢弃草稿（提交成功或离开表单时调用） */
export const clearPageDraft = (): void => {
  memoryDraft = null
  writeToStorage(null)
}

/** 从路由 query 里取出令牌；同名参数出现多次时取第一个 */
export const draftTokenFromQuery = (
  value: string | null | undefined | (string | null)[]
): string | null => {
  const token = Array.isArray(value) ? value[0] : value
  return token || null
}
