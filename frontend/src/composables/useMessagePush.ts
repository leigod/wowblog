/**
 * 消息推送组合式函数
 * 根据系统配置自动选择 WebSocket 或轮询方式
 */
import { onMounted, onUnmounted, ref } from 'vue'
import { useAppStore } from '@/stores/app'
import { wsService } from '@/api/services/websocket'
import type { WebSocketMessage } from '@/api/services/websocket'

export interface MessagePushOptions {
  /** 是否在组件挂载时自动启动 */
  autoStart?: boolean
  /** WebSocket 消息类型监听 */
  messageTypes?: string[]
  /** 自定义消息处理函数 */
  onMessage?: (message: WebSocketMessage) => void
  /** 新消息回调 */
  onNewMessage?: (data: any) => void
}

export function useMessagePush(options: MessagePushOptions = {}) {
  const {
    autoStart = true,
    messageTypes = ['new_message', 'notification'],
    onMessage,
    onNewMessage
  } = options

  const appStore = useAppStore()
  const pollingTimer = ref<any>(null)
  const isConnected = ref(false)
  const messageCount = ref(0)

  /**
   * 启动消息推送
   */
  const start = async () => {
    // 加载公共配置
    await appStore.loadPublicConfig()

    // 根据配置选择推送方式
    if (appStore.messagePushMethod === 'websocket') {
      startWebSocket()
    } else {
      startPolling()
    }
  }

  /**
   * 停止消息推送
   */
  const stop = () => {
    stopWebSocket()
    stopPolling()
  }

  /**
   * 重启消息推送（配置变更时调用）
   */
  const restart = async () => {
    stop()
    await appStore.loadPublicConfig()
    start()
  }

  /**
   * 启动 WebSocket
   */
  const startWebSocket = () => {
    console.log('[消息推送] 启动 WebSocket 模式')

    // 构建 WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/ws/messages`

    // 连接 WebSocket
    wsService.connect(wsUrl, appStore.token || undefined)

    // 监听连接状态
    wsService.on('connected', () => {
      isConnected.value = true
      console.log('[消息推送] WebSocket 已连接')
    })

    wsService.on('reconnecting', () => {
      isConnected.value = false
      console.log('[消息推送] WebSocket 重连中...')
    })

    // 监听新消息
    messageTypes.forEach(type => {
      wsService.on(type, (data) => {
        messageCount.value++
        if (onNewMessage) {
          onNewMessage(data)
        }
        if (onMessage) {
          onMessage({ type, data, timestamp: Date.now() })
        }
      })
    })
  }

  /**
   * 停止 WebSocket
   */
  const stopWebSocket = () => {
    wsService.disconnect()
    isConnected.value = false
    console.log('[消息推送] WebSocket 已断开')
  }

  /**
   * 启动轮询模式
   */
  const startPolling = () => {
    console.log('[消息推送] 启动轮询模式，间隔:', appStore.pollingInterval)

    // 立即执行一次
    fetchMessages()

    // 设置定时轮询
    pollingTimer.value = setInterval(() => {
      fetchMessages()
    }, appStore.pollingInterval)
  }

  /**
   * 停止轮询
   */
  const stopPolling = () => {
    if (pollingTimer.value) {
      clearInterval(pollingTimer.value)
      pollingTimer.value = null
      console.log('[消息推送] 轮询已停止')
    }
  }

  /**
   * 获取消息（轮询模式使用）
   */
  const fetchMessages = async () => {
    try {
      // 这里调用获取消息的 API
      // const response = await getMessages()
      // if (response.data && response.data.length > 0) {
      //   messageCount.value = response.data.length
      //   if (onNewMessage) {
      //     response.data.forEach((msg: any) => onNewMessage(msg))
      //   }
      // }
    } catch (error) {
      console.error('[消息推送] 获取消息失败:', error)
    }
  }

  /**
   * 获取当前推送方式
   */
  const getPushMethod = () => {
    return appStore.messagePushMethod
  }

  /**
   * 是否使用 WebSocket
   */
  const isWebSocketMode = () => {
    return appStore.messagePushMethod === 'websocket'
  }

  /**
   * 组件挂载时自动启动
   */
  onMounted(() => {
    if (autoStart) {
      start()
    }
  })

  /**
   * 组件卸载时清理
   */
  onUnmounted(() => {
    stop()
  })

  return {
    isConnected,
    messageCount,
    start,
    stop,
    restart,
    getPushMethod,
    isWebSocketMode
  }
}
