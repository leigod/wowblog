/**
 * 生成字母头像的公共函数
 * @param name 用户名或全名
 * @returns SVG代码，可以直接用在img标签的src属性
 */
export const generateLetterAvatar = (name: string): string => {
  if (!name || typeof name !== 'string' || name.trim() === '') {
    // 提供默认头像
    return generateDefaultAvatar()
  }

  // 提取首字母
  const initials = getInitials(name)

  // 随机选择一个背景色
  const backgroundColor = getRandomBackgroundColor()

  // 生成SVG代码
  const svg = generateSvg(initials, backgroundColor)

  // 将SVG转换为data URL格式
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`
}

/**
 * 提取名称的首字母
 * @param name 输入名称
 * @returns 提取的首字母（一个或两个）
 */
const getInitials = (name: string): string => {
  // 移除所有多余空格
  const trimmedName = name.trim()

  // 按空格分割名称
  const nameParts = trimmedName.split(/\s+/)

  if (nameParts.length === 0) {
    return 'U' // 未知用户
  }

  // 如果只有一个单词，取首字母
  if (nameParts.length === 1) {
    return nameParts[0].charAt(0).toUpperCase()
  }

  // 如果有多个单词，取前两个单词的首字母
  return `${nameParts[0].charAt(0)}${nameParts[1].charAt(0)}`.toUpperCase()
}

/**
 * 从预定义的颜色列表中随机选择一个背景色
 * @returns 随机背景色的十六进制值
 */
const getRandomBackgroundColor = (): string => {
  // 预定义的清新自然的颜色列表（赤橙黄绿青蓝紫的不同色调）
  const colors = [
    '#FFB3BA', // 浅红色
    '#FFDFBA', // 浅橙色
    '#FFFFBA', // 浅黄色
    '#BAFFC9', // 浅绿色
    '#BAE1FF', // 浅蓝色
    '#D4BAFF', // 浅紫色
    '#FFBAF2', // 浅粉色
    '#FFD8BA', // 浅珊瑚色
    '#E8F5E9', // 浅薄荷绿
    '#E0F7FA', // 浅蓝色
    '#E8EAF6', // 浅靛蓝色
    '#F3E5F5', // 浅紫色
    '#FFF8E1', // 浅琥珀色
    '#F1F8E9', // 浅绿色
    '#E0F2F1', // 浅青色
    '#E3F2FD', // 浅蓝色
    '#F5F5F5', // 浅灰色
    '#FCE4EC', // 浅粉色
    '#FBE9E7', // 浅红色
    '#FFF3E0', // 浅橙色
    '#FFFDE7', // 浅黄色
    '#E8F5E9', // 浅绿色
    '#E8F5E9', // 浅绿色
    '#E0F7FA', // 浅蓝色
    '#F3E5F5' // 浅紫色
  ]

  // 随机选择一个颜色
  const randomIndex = Math.floor(Math.random() * colors.length)
  return colors[randomIndex]
}

/**
 * 生成SVG代码
 * @param initials 首字母
 * @param backgroundColor 背景色
 * @returns SVG字符串
 */
const generateSvg = (initials: string, backgroundColor: string): string => {
  const size = 160 // SVG尺寸
  const fontSize = initials.length === 1 ? size / 2 : size / 2.5 // 根据字母数量调整字体大小
  const fontWeight = 'bold'
  const textColor = '#000000' // 文字颜色始终为白色，以确保在彩色背景上的可读性

  // SVG代码模板
  return `<svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
    <rect width="${size}" height="${size}" fill="${backgroundColor}" />
    <text 
      x="50%" 
      y="55%" 
      font-family="Arial, sans-serif" 
      font-size="${fontSize}" 
      font-weight="${fontWeight}" 
      fill="${textColor}" 
      text-anchor="middle" 
      dominant-baseline="middle" 
    >
      ${initials}
    </text>
  </svg>`
}

/**
 * 生成默认头像
 * @returns 默认头像的data URL
 */
const generateDefaultAvatar = (): string => {
  return generateSvg('U', '#E0E0E0') // 使用灰色背景的默认头像
}
