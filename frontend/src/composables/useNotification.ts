import { ref } from 'vue'

export interface NotificationItem {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  closable?: boolean
  timestamp: number
}

const notifications = ref<NotificationItem[]>([])
let notificationId = 0

export function useNotification() {
  const showNotification = (
    title: string,
    type: NotificationItem['type'] = 'info',
    options: Partial<NotificationItem> = {},
  ) => {
    const notification: NotificationItem = {
      id: `notification-${++notificationId}`,
      type,
      title,
      message: options.message,
      duration: options.duration ?? (type === 'error' ? 0 : 4000),
      closable: options.closable ?? true,
      timestamp: Date.now(),
    }

    notifications.value.push(notification)

    // 自动关闭
    if (notification.duration && notification.duration > 0) {
      setTimeout(() => {
        removeNotification(notification.id)
      }, notification.duration)
    }

    return notification.id
  }

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    notifications.value.length = 0
  }

  // 便捷方法
  const success = (title: string, message?: string, duration?: number) => {
    return showNotification(title, 'success', { message, duration })
  }

  const error = (title: string, message?: string, duration?: number) => {
    return showNotification(title, 'error', { message, duration })
  }

  const warning = (title: string, message?: string, duration?: number) => {
    return showNotification(title, 'warning', { message, duration })
  }

  const info = (title: string, message?: string, duration?: number) => {
    return showNotification(title, 'info', { message, duration })
  }

  return {
    notifications,
    showNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info,
  }
}
