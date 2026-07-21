/**
 * WebSocket 服务
 * 用于实时消息推送
 */

export interface WebSocketMessage {
  type: string
  data?: any
  timestamp?: number
}

export type MessageHandler = (data: any) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectTimer: any = null
  private heartbeatTimer: any = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private messageHandlers: Map<string, MessageHandler[]> = new Map()
  private isManualClose = false
  private url: string = ''

  /**
   * 连接 WebSocket
   * @param url WebSocket 服务器地址
   * @param token 认证 token
   */
  connect(url: string, token?: string): void {
    // 如果已有连接，先断开
    if (this.ws) {
      this.disconnect()
    }

    this.isManualClose = false
    this.url = url

    try {
      // 构建 WebSocket URL，支持 token 参数
      const wsUrl = token ? `${url}?token=${token}` : url
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('[WebSocket] 连接成功')
        this.reconnectAttempts = 0
        this.reconnectDelay = 1000

        // 启动心跳
        this.startHeartbeat()

        // 触发连接成功事件
        this.emit('connected', { timestamp: Date.now() })
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('[WebSocket] 消息解析失败:', error)
        }
      }

      this.ws.onclose = (event) => {
        console.log('[WebSocket] 连接关闭', event.code, event.reason)
        this.cleanup()

        // 如果不是手动关闭，尝试重连
        if (!this.isManualClose) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error('[WebSocket] 连接错误:', error)
      }
    } catch (error) {
      console.error('[WebSocket] 创建连接失败:', error)
      this.scheduleReconnect()
    }
  }

  /**
   * 断开 WebSocket 连接
   */
  disconnect(): void {
    this.isManualClose = true
    this.cleanup()

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  /**
   * 发送消息
   * @param message 消息对象
   */
  send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('[WebSocket] 连接未建立，无法发送消息')
    }
  }

  /**
   * 监听消息
   * @param type 消息类型
   * @param handler 处理函数
   */
  on(type: string, handler: MessageHandler): void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, [])
    }
    this.messageHandlers.get(type)!.push(handler)
  }

  /**
   * 取消监听
   * @param type 消息类型
   * @param handler 处理函数
   */
  off(type: string, handler: MessageHandler): void {
    const handlers = this.messageHandlers.get(type)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  /**
   * 获取连接状态
   */
  getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }

  /**
   * 是否已连接
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WebSocketMessage): void {
    const { type, data } = message

    // 处理心跳响应
    if (type === 'pong') {
      return
    }

    // 分发消息到对应的处理器
    const handlers = this.messageHandlers.get(type) || []
    handlers.forEach(handler => {
      try {
        handler(data)
      } catch (error) {
        console.error(`[WebSocket] 消息处理器错误 (${type}):`, error)
      }
    })

    // 通用消息处理器
    const allHandlers = this.messageHandlers.get('*') || []
    allHandlers.forEach(handler => {
      try {
        handler({ type, data })
      } catch (error) {
        console.error('[WebSocket] 通用消息处理器错误:', error)
      }
    })
  }

  /**
   * 触发事件
   */
  private emit(type: string, data?: any): void {
    const handlers = this.messageHandlers.get(type) || []
    handlers.forEach(handler => {
      try {
        handler(data)
      } catch (error) {
        console.error(`[WebSocket] 事件处理器错误 (${type}):`, error)
      }
    })
  }

  /**
   * 启动心跳
   */
  private startHeartbeat(): void {
    this.cleanupHeartbeat()

    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'ping' })
      }
    }, 30000) // 每30秒发送一次心跳
  }

  /**
   * 清理心跳定时器
   */
  private cleanupHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * 清理资源
   */
  private cleanup(): void {
    this.cleanupHeartbeat()
  }

  /**
   * 安排重连
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] 达到最大重连次数，停止重连')
      this.emit('max_reconnect_reached')
      return
    }

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }

    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000)

    console.log(`[WebSocket] ${delay}ms 后尝试第 ${this.reconnectAttempts} 次重连`)

    this.reconnectTimer = setTimeout(() => {
      console.log(`[WebSocket] 开始第 ${this.reconnectAttempts} 次重连`)
      this.connect(this.url)
    }, delay)

    // 触发重连事件
    this.emit('reconnecting', { attempt: this.reconnectAttempts, delay })
  }
}

// 导出单例
export const wsService = new WebSocketService()
