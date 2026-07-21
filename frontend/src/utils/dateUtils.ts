// 时间戳格式化函数
export const formatDateTime = (
  timestamp: number | string,
  format: string | null = 'YYYY-MM-DD HH:mm:ss'
): string => {
  // 确保timestamp是数字类型
  const ts = typeof timestamp === 'string' ? parseInt(timestamp) : timestamp

  if (!ts || isNaN(ts)) {
    return ''
  }

  // 判断时间戳是秒级还是毫秒级，如果是秒级则转换为毫秒级
  let timestampMs = ts
  // 如果时间戳小于等于10位数字，很可能是秒级时间戳
  if (ts.toString().length <= 10) {
    timestampMs = ts * 1000
  }

  const date = new Date(timestampMs)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')

  if (format) {
    return format
      .replace('YYYY', `${year}`)
      .replace('MM', `${month}`)
      .replace('DD', `${day}`)
      .replace('HH:mm', `${hours}:${minutes}`)
      .replace(':ss', `${seconds}`)
  } else {
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }
}
