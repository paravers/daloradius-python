<template>
  <div class="forgot-password-container">
    <div class="forgot-password-form-container">
      <div class="forgot-password-header">
        <h1>忘记密码</h1>
        <p>请输入您的邮箱地址，我们将发送验证码到您的邮箱</p>
      </div>
      
      <!-- 步骤1: 输入邮箱 -->
      <a-form
        v-if="step === 1"
        :model="formData"
        :rules="emailRules"
        @finish="handleSendCode"
        layout="vertical"
        class="forgot-password-form"
      >
        <a-form-item name="email" label="邮箱地址">
          <a-input
            v-model:value="formData.email"
            size="large"
            type="email"
            placeholder="请输入您的邮箱地址"
            :prefix="h(MailOutlined)"
          />
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            block
            :loading="loading"
          >
            发送验证码
          </a-button>
        </a-form-item>

        <div class="form-links">
          <a-space>
            <router-link to="/auth/login">返回登录</router-link>
            <a-divider type="vertical" />
            <router-link to="/auth/register">注册账户</router-link>
          </a-space>
        </div>
      </a-form>

      <!-- 步骤2: 输入验证码和新密码 -->
      <a-form
        v-if="step === 2"
        :model="resetData"
        :rules="resetRules"
        @finish="handleResetPassword"
        layout="vertical"
        class="forgot-password-form"
      >
        <a-alert
          :message="`验证码已发送到 ${formData.email}`"
          type="success"
          show-icon
          style="margin-bottom: 24px"
        />

        <a-form-item name="verificationCode" label="验证码">
          <a-input
            v-model:value="resetData.verificationCode"
            size="large"
            placeholder="请输入6位验证码"
            :prefix="h(SafetyOutlined)"
            maxlength="6"
          />
        </a-form-item>

        <a-form-item name="newPassword" label="新密码">
          <a-input-password
            v-model:value="resetData.newPassword"
            size="large"
            placeholder="请输入新密码（至少6位）"
            :prefix="h(LockOutlined)"
          />
        </a-form-item>

        <a-form-item name="confirmPassword" label="确认新密码">
          <a-input-password
            v-model:value="resetData.confirmPassword"
            size="large"
            placeholder="请再次输入新密码"
            :prefix="h(LockOutlined)"
          />
        </a-form-item>

        <a-form-item>
          <a-space direction="vertical" style="width: 100%">
            <a-button
              type="primary"
              html-type="submit"
              size="large"
              block
              :loading="loading"
            >
              重置密码
            </a-button>
            
            <a-button
              size="large"
              block
              @click="handleResendCode"
              :loading="resendLoading"
              :disabled="countdown > 0"
            >
              {{ countdown > 0 ? `重新发送 (${countdown}s)` : '重新发送验证码' }}
            </a-button>
          </a-space>
        </a-form-item>

        <div class="form-links">
          <a-space>
            <a @click="goBackToStep1">返回上一步</a>
            <a-divider type="vertical" />
            <router-link to="/auth/login">返回登录</router-link>
          </a-space>
        </div>
      </a-form>

      <!-- 步骤3: 成功提示 -->
      <div v-if="step === 3" class="success-container">
        <a-result
          status="success"
          title="密码重置成功！"
          sub-title="您的密码已成功重置，请使用新密码登录"
        >
          <template #extra>
            <a-button type="primary" size="large" @click="goToLogin">
              立即登录
            </a-button>
          </template>
        </a-result>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { MailOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons-vue'
import { authService } from '@/services'

const router = useRouter()

const loading = ref(false)
const resendLoading = ref(false)
const step = ref(1)
const countdown = ref(0)
let countdownTimer: NodeJS.Timeout | null = null

const formData = reactive({
  email: ''
})

const resetData = reactive({
  verificationCode: '',
  newPassword: '',
  confirmPassword: ''
})

const emailRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

const resetRules = {
  verificationCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码必须是6位数字', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '验证码必须是6位数字', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 256, message: '密码长度应为6-256个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string) => {
        if (value && value !== resetData.newPassword) {
          return Promise.reject('两次输入的密码不一致')
        }
        return Promise.resolve()
      },
      trigger: 'blur'
    }
  ]
}

const startCountdown = () => {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer!)
      countdownTimer = null
    }
  }, 1000)
}

const handleSendCode = async () => {
  try {
    loading.value = true
    
    await authService.sendVerificationCode(formData.email)
    
    message.success('验证码已发送到您的邮箱，请查收')
    step.value = 2
    startCountdown()
    
  } catch (error: any) {
    console.error('Send verification code failed:', error)
    
    const errorMessage = error?.response?.data?.detail || 
                        error?.message || 
                        '发送验证码失败，请稍后再试'
    
    message.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const handleResendCode = async () => {
  try {
    resendLoading.value = true
    
    await authService.sendVerificationCode(formData.email)
    
    message.success('验证码已重新发送')
    startCountdown()
    
  } catch (error: any) {
    console.error('Resend verification code failed:', error)
    
    const errorMessage = error?.response?.data?.detail || 
                        error?.message || 
                        '重新发送验证码失败，请稍后再试'
    
    message.error(errorMessage)
  } finally {
    resendLoading.value = false
  }
}

const handleResetPassword = async () => {
  try {
    loading.value = true
    
    await authService.resetPassword({
      email: formData.email,
      verificationCode: resetData.verificationCode,
      newPassword: resetData.newPassword
    })
    
    message.success('密码重置成功！')
    step.value = 3
    
  } catch (error: any) {
    console.error('Reset password failed:', error)
    
    const errorMessage = error?.response?.data?.detail || 
                        error?.message || 
                        '密码重置失败，请检查验证码是否正确'
    
    message.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const goBackToStep1 = () => {
  step.value = 1
  resetData.verificationCode = ''
  resetData.newPassword = ''
  resetData.confirmPassword = ''
  
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
    countdown.value = 0
  }
}

const goToLogin = () => {
  router.push('/auth/login')
}

// 清理定时器
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.forgot-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.forgot-password-form-container {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(50, 50, 93, 0.1), 0 5px 15px rgba(0, 0, 0, 0.07);
  width: 100%;
  max-width: 450px;
}

.forgot-password-header {
  text-align: center;
  margin-bottom: 32px;
}

.forgot-password-header h1 {
  color: #1890ff;
  margin-bottom: 8px;
  font-size: 28px;
  font-weight: 600;
}

.forgot-password-header p {
  color: #8c8c8c;
  font-size: 14px;
  margin: 0;
  line-height: 1.5;
}

.forgot-password-form {
  width: 100%;
}

.form-links {
  text-align: center;
  margin-top: 16px;
}

.form-links a {
  color: #1890ff;
  text-decoration: none;
  cursor: pointer;
}

.form-links a:hover {
  text-decoration: underline;
}

.success-container {
  text-align: center;
}

@media (max-width: 768px) {
  .forgot-password-form-container {
    padding: 24px;
    margin: 0 16px;
  }
  
  .forgot-password-header h1 {
    font-size: 24px;
  }
  
  .forgot-password-header p {
    font-size: 13px;
  }
}
</style>