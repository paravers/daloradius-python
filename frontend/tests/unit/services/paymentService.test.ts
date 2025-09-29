import { describe, it, expect, beforeEach } from 'vitest'
import { paymentService } from '@/services/paymentService'
import type { CreatePaymentRequest, RefundRequest } from '@/types/billing'

describe('PaymentService', () => {
  beforeEach(() => {
    // Reset mock data before each test
    // In a real implementation, you might want to reset the service state
  })

  describe('getPayments', () => {
    it('should return list of payments', async () => {
      const result = await paymentService.getPayments()
      
      expect(result).toHaveProperty('data')
      expect(result).toHaveProperty('total')
      expect(result).toHaveProperty('page')
      expect(result).toHaveProperty('pageSize')
      expect(Array.isArray(result.data)).toBe(true)
    })

    it('should filter payments by status', async () => {
      const result = await paymentService.getPayments({
        status: 'completed'
      })
      
      expect(result.data.every(payment => payment.status === 'completed')).toBe(true)
    })

    it('should filter payments by payment method', async () => {
      const result = await paymentService.getPayments({
        paymentMethodType: 'alipay'
      })
      
      expect(result.data.every(payment => payment.paymentMethodType === 'alipay')).toBe(true)
    })
  })

  describe('createPayment', () => {
    it('should create a new payment', async () => {
      const paymentData: CreatePaymentRequest = {
        userId: 'test-user',
        invoiceId: 'test-invoice',
        userInfo: {
          name: '测试用户',
          email: 'test@example.com',
          phone: '13800138000'
        },
        amount: {
          amount: 100.00,
          currency: 'CNY'
        },
        paymentMethodType: 'alipay',
        gatewayType: 'alipay',
        description: '测试支付',
        metadata: {}
      }

      const result = await paymentService.createPayment(paymentData)
      
      expect(result.success).toBe(true)
      expect(result.payment).toBeDefined()
      expect(result.payment?.amount.amount).toBe(100.00)
      expect(result.payment?.status).toBe('pending')
    })

    it('should validate payment request', () => {
      const invalidData: CreatePaymentRequest = {
        userId: '',
        invoiceId: '',
        userInfo: {
          name: '',
          email: 'invalid-email',
          phone: ''
        },
        amount: {
          amount: 0,
          currency: 'CNY'
        },
        paymentMethodType: 'alipay',
        gatewayType: 'alipay',
        description: '',
        metadata: {}
      }

      const validation = paymentService.validatePaymentRequest(invalidData)
      
      expect(validation.valid).toBe(false)
      expect(validation.errors.length).toBeGreaterThan(0)
    })
  })

  describe('processPayment', () => {
    it('should process a pending payment', async () => {
      // First create a payment
      const paymentData: CreatePaymentRequest = {
        userId: 'test-user',
        invoiceId: 'test-invoice',
        userInfo: {
          name: '测试用户',
          email: 'test@example.com',
          phone: '13800138000'
        },
        amount: {
          amount: 50.00,
          currency: 'CNY'
        },
        paymentMethodType: 'alipay',
        gatewayType: 'alipay',
        description: '测试支付处理',
        metadata: {}
      }

      const createResult = await paymentService.createPayment(paymentData)
      expect(createResult.success).toBe(true)
      
      const paymentId = createResult.payment!.id
      
      // Then process it
      const processResult = await paymentService.processPayment(paymentId)
      
      expect(processResult).toHaveProperty('success')
      expect(processResult).toHaveProperty('payment')
      expect(processResult).toHaveProperty('message')
    })
  })

  describe('createRefund', () => {
    it('should create a refund request', async () => {
      // First create and complete a payment
      const paymentData: CreatePaymentRequest = {
        userId: 'test-user',
        invoiceId: 'test-invoice',
        userInfo: {
          name: '测试用户',
          email: 'test@example.com',
          phone: '13800138000'
        },
        amount: {
          amount: 200.00,
          currency: 'CNY'
        },
        paymentMethodType: 'alipay',
        gatewayType: 'alipay',
        description: '测试退款支付',
        metadata: {}
      }

      const createResult = await paymentService.createPayment(paymentData)
      expect(createResult.success).toBe(true)
      
      const paymentId = createResult.payment!.id
      
      // Mark payment as completed
      await paymentService.markPaymentCompleted(paymentId, 'test-transaction-id')
      
      // Create refund request
      const refundData: RefundRequest = {
        paymentId: paymentId,
        amount: {
          amount: 100.00,
          currency: 'CNY'
        },
        reason: '用户申请退款',
        metadata: {}
      }

      const refundResult = await paymentService.createRefund(refundData)
      
      expect(refundResult.success).toBe(true)
      expect(refundResult.refund).toBeDefined()
      expect(refundResult.refund?.amount.amount).toBe(100.00)
      expect(refundResult.refund?.status).toBe('pending')
    })

    it('should validate refund request', () => {
      const invalidRefundData: RefundRequest = {
        paymentId: '',
        amount: {
          amount: 0,
          currency: 'CNY'
        },
        reason: 'abc', // Too short
        metadata: {}
      }

      const validation = paymentService.validateRefundRequest(invalidRefundData)
      
      expect(validation.valid).toBe(false)
      expect(validation.errors.length).toBeGreaterThan(0)
    })
  })

  describe('getPaymentStatistics', () => {
    it('should return payment statistics', async () => {
      const stats = await paymentService.getPaymentStatistics()
      
      expect(stats).toHaveProperty('totalAmount')
      expect(stats).toHaveProperty('totalCount')
      expect(stats).toHaveProperty('completedAmount')
      expect(stats).toHaveProperty('completedCount')
      expect(stats).toHaveProperty('conversionRate')
      expect(typeof stats.totalCount).toBe('number')
      expect(typeof stats.completedCount).toBe('number')
      expect(typeof stats.conversionRate).toBe('number')
    })
  })

  describe('getPaymentMethodStatistics', () => {
    it('should return payment method statistics', async () => {
      const methodStats = await paymentService.getPaymentMethodStatistics()
      
      expect(Array.isArray(methodStats)).toBe(true)
      
      if (methodStats.length > 0) {
        const stat = methodStats[0]
        expect(stat).toHaveProperty('paymentMethodType')
        expect(stat).toHaveProperty('amount')
        expect(stat).toHaveProperty('count')
        expect(stat).toHaveProperty('percentage')
      }
    })
  })
})