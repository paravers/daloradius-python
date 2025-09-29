import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PaymentsView from '@/views/billing/PaymentsView.vue'
import { usePayments } from '@/composables/usePayments'

// Mock the composable
vi.mock('@/composables/usePayments', () => ({
  usePayments: vi.fn(() => ({
    payments: [],
    total: 0,
    loading: false,
    pagination: { page: 1, pageSize: 10 },
    queryParams: {},
    statistics: null,
    loadPayments: vi.fn(),
    deletePayment: vi.fn(),
    processPayment: vi.fn(),
    cancelPayment: vi.fn(),
    retryPayment: vi.fn(),
    loadStatistics: vi.fn(),
    setPage: vi.fn(),
    setPageSize: vi.fn()
  }))
}))

describe('PaymentsView', () => {
  it('should render page title', () => {
    const wrapper = mount(PaymentsView)
    
    expect(wrapper.find('.page-title').text()).toBe('支付管理')
  })

  it('should render create payment button', () => {
    const wrapper = mount(PaymentsView)
    
    const createButton = wrapper.find('button').filter(btn => 
      btn.text().includes('创建支付')
    )
    
    expect(createButton.exists()).toBe(true)
  })

  it('should call loadPayments on mount', () => {
    const mockLoadPayments = vi.fn()
    const mockLoadStatistics = vi.fn()
    
    vi.mocked(usePayments).mockReturnValue({
      payments: [],
      total: 0,
      loading: false,
      pagination: { page: 1, pageSize: 10 },
      queryParams: {},
      statistics: null,
      loadPayments: mockLoadPayments,
      deletePayment: vi.fn(),
      processPayment: vi.fn(),
      cancelPayment: vi.fn(),
      retryPayment: vi.fn(),
      loadStatistics: mockLoadStatistics,
      setPage: vi.fn(),
      setPageSize: vi.fn()
    } as any)

    mount(PaymentsView)
    
    expect(mockLoadPayments).toHaveBeenCalled()
    expect(mockLoadStatistics).toHaveBeenCalled()
  })
})