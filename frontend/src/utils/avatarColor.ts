/**
 * 头像主色提取工具
 *
 * 用 canvas 从头像图片中提取主色调，用于个人资料页头部
 * 通栏背景的动态渐变。SVG dataURL 与同源图片可直接取色；
 * 跨域图片会触发 canvas 污染检测，自动回退到用户名 hash 配色。
 */

/** 精选自然色板（与 avatarUtils 保持同一色系，作为回退配色） */
const FALLBACK_COLORS = [
  '#2e7d6b', // 松绿
  '#3a6ea5', // 黛蓝
  '#8a5a9e', // 藤紫
  '#b06a3b', // 陶橙
  '#5b8c5a', // 苔绿
  '#a34f68', // 绛红
  '#4a7dab', // 青蓝
  '#7a6a52' // 棕褐
]

/** 根据用户名生成稳定的回退颜色 */
const hashColor = (name: string): string => {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) | 0
  }
  return FALLBACK_COLORS[Math.abs(hash) % FALLBACK_COLORS.length]
}

/** hex -> {h,s,l} (h:0-360, s/l:0-1) */
const hexToHsl = (hex: string): { h: number; s: number; l: number } => {
  const r = parseInt(hex.slice(1, 3), 16) / 255
  const g = parseInt(hex.slice(3, 5), 16) / 255
  const b = parseInt(hex.slice(5, 7), 16) / 255
  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  const l = (max + min) / 2
  if (max === min) return { h: 0, s: 0, l }
  const d = max - min
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
  let h = 0
  if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6
  else if (max === g) h = ((b - r) / d + 2) / 6
  else h = ((r - g) / d + 4) / 6
  return { h: h * 360, s, l }
}

/** {h,s,l} -> hex */
const hslToHex = (h: number, s: number, l: number): string => {
  const hue = ((h % 360) + 360) % 360
  const c = (1 - Math.abs(2 * l - 1)) * s
  const x = c * (1 - Math.abs(((hue / 60) % 2) - 1))
  const m = l - c / 2
  let r = 0
  let g = 0
  let b = 0
  if (hue < 60) [r, g, b] = [c, x, 0]
  else if (hue < 120) [r, g, b] = [x, c, 0]
  else if (hue < 180) [r, g, b] = [0, c, x]
  else if (hue < 240) [r, g, b] = [0, x, c]
  else if (hue < 300) [r, g, b] = [x, 0, c]
  else [r, g, b] = [c, 0, x]
  const toHex = (v: number) =>
    Math.round((v + m) * 255)
      .toString(16)
      .padStart(2, '0')
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

/**
 * 从图片提取主色（返回 hex）
 * 取饱和度 × 权重最高的色相桶的均值，灰图返回 null
 */
const extractDominantColor = (img: HTMLImageElement): string | null => {
  const SIZE = 48
  const canvas = document.createElement('canvas')
  canvas.width = SIZE
  canvas.height = SIZE
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  if (!ctx) return null
  ctx.drawImage(img, 0, 0, SIZE, SIZE)

  let data: Uint8ClampedArray
  try {
    data = ctx.getImageData(0, 0, SIZE, SIZE).data
  } catch {
    // canvas 被跨域图片污染
    return null
  }

  // 12 个色相桶，按 饱和度×数量 累计权重
  const buckets: Array<{ weight: number; r: number; g: number; b: number; count: number }> =
    Array.from({ length: 12 }, () => ({ weight: 0, r: 0, g: 0, b: 0, count: 0 }))
  let grayish = 0
  let total = 0

  for (let i = 0; i < data.length; i += 4) {
    const a = data[i + 3]
    if (a < 128) continue
    const r = data[i]
    const g = data[i + 1]
    const b = data[i + 2]
    total++
    const max = Math.max(r, g, b) / 255
    const min = Math.min(r, g, b) / 255
    const l = (max + min) / 2
    const d = max - min
    const s = max === min ? 0 : l > 0.5 ? d / (2 - max - min) : d / (max + min)
    // 忽略接近纯白/纯黑/纯灰的像素
    if (s < 0.12 || l < 0.08 || l > 0.96) {
      grayish++
      continue
    }
    let h = 0
    if (max === min) h = 0
    else if (max === r / 255) h = ((g - b) / 255 / d + (g < b ? 6 : 0)) / 6
    else if (max === g / 255) h = ((b - r) / 255 / d + 2) / 6
    else h = ((r - g) / 255 / d + 4) / 6
    const bin = Math.floor(h * 12) % 12
    const weight = s * (1 - Math.abs(l - 0.5) * 0.8)
    buckets[bin].weight += weight
    buckets[bin].r += r
    buckets[bin].g += g
    buckets[bin].b += b
    buckets[bin].count++
  }

  if (total === 0) return null
  // 彩色像素占比过低，视为灰图
  if (total - grayish < total * 0.08) return null

  let best = -1
  let bestWeight = 0
  for (let i = 0; i < 12; i++) {
    if (buckets[i].count > 0 && buckets[i].weight > bestWeight) {
      bestWeight = buckets[i].weight
      best = i
    }
  }
  if (best < 0) return null
  const bk = buckets[best]
  const toHex = (v: number) =>
    Math.round(v / bk.count)
      .toString(16)
      .padStart(2, '0')
  return `#${toHex(bk.r)}${toHex(bk.g)}${toHex(bk.b)}`
}

export interface HeroPalette {
  /** 主色（用于图标点缀等） */
  base: string
  /** 浅色主题渐变起点（柔和浅色调） */
  light: string
  /** 浅色主题渐变终点（更浅、接近画布色） */
  lightSoft: string
  /** 深色主题渐变起点（低亮度深色调） */
  dark: string
  /** 深色主题渐变终点（更深） */
  darkSoft: string
}

/** 由一个基色推导整套 hero 渐变色板 */
const buildPalette = (base: string): HeroPalette => {
  const { h, s } = hexToHsl(base)
  const sat = Math.min(Math.max(s, 0.28), 0.6)
  return {
    base,
    light: hslToHex(h, sat, 0.86),
    lightSoft: hslToHex(h, sat * 0.7, 0.94),
    dark: hslToHex(h, sat * 0.85, 0.22),
    darkSoft: hslToHex(h, sat * 0.6, 0.14)
  }
}

/**
 * 提取头像主色并生成 hero 配色。
 * - 头像取色失败（跨域/加载失败/灰图）时回退到用户名 hash 配色
 * @param avatarSrc 头像地址（dataURL 或 URL）
 * @param username 用户名（回退 hash 用）
 */
export const getHeroPalette = async (
  avatarSrc: string | undefined | null,
  username: string
): Promise<HeroPalette> => {
  const fallback = () => buildPalette(hashColor(username || 'user'))

  if (!avatarSrc) return fallback()

  // dataURL 直接加载；同源/代理路径无跨域问题
  return new Promise<HeroPalette>((resolve) => {
    const img = new Image()
    let settled = false
    const finish = (color: string | null) => {
      if (settled) return
      settled = true
      resolve(color ? buildPalette(color) : fallback())
    }
    img.onload = () => {
      try {
        finish(extractDominantColor(img))
      } catch {
        finish(null)
      }
    }
    img.onerror = () => finish(null)
    // 兜底超时：800ms 内未完成则走回退
    setTimeout(() => finish(null), 800)
    img.src = avatarSrc
  })
}
