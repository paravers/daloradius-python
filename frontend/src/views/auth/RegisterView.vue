<template>
  <div class="register-container">
    <div class="register-form-container">
      <div class="register-header">
        <h1>注册账户</h1>
        <p>创建您的 daloRADIUS 账户</p>
      </div>
      
      <a-form
        :model="formData"
        :rules="rules"
        @finish="handleSubmit"
        layout="vertical"
        class="register-form"
      >
        <a-form-item name="username" label="用户名">
          <a-input
            v-model:value="formData.username"
            size="large"
            placeholder="请输入用户名"
            :prefix="h(UserOutlined)"
          />
        </a-form-item>

        <a-form-item name="email" label="邮箱">
          <a-input
            v-model:value="formData.email"
            size="large"
            type="email"
            placeholder="请输入邮箱地址"
            :prefix="h(MailOutlined)"
          />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item name="firstName" label="名">
              <a-input
                v-model:value="formData.firstName"
                size="large"
                placeholder="请输入名"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item name="lastName" label="姓">
              <a-input
                v-model:value="formData.lastName"
                size="large"
                placeholder="请输入姓"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item name="password" label="密码">
          <a-input-password
            v-model:value="formData.password"
            size="large"
            placeholder="请输入密码（至少6位）"
            :prefix="h(LockOutlined)"
          />
        </a-form-item>

        <a-form-item name="confirmPassword" label="确认密码">
          <a-input-password
            v-model:value="formData.confirmPassword"
            size="large"
            placeholder="请再次输入密码"
            :prefix="h(LockOutlined)"
          />
        </a-form-item>

        <a-form-item name="agreement">
          <a-checkbox v-model:checked="formData.agreement">
            我已阅读并同意 <a href="#" @click.prevent>服务条款</a> 和 <a href="#" @click.prevent>隐私政策</a>
          </a-checkbox>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            block
            :loading="loading"
          >
            注册
          </a-button>
        </a-form-item>

        <div class="register-links">
          <a-space>
            <span>已有账户？</span>
            <router-link to="/auth/login">立即登录</router-link>
          </a-space>
        </div>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import type { RegisterForm } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)

const formData = reactive<RegisterForm & { confirmPassword: string; agreement: boolean }>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  firstName: '',
  lastName: '',
  agreement: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 64, message: '用户名长度应为3-64个字符', trigger: 'blur' },
    { 
      pattern: /^[A-Za-z0-9._@-]+$/, 
      message: '用户名只能包含字母、数字、点、下划线、@和连字符', 
      trigger: 'blur' 
    }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 256, message: '密码长度应为6-256个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string) => {
        if (value && value !== formData.password) {
          return Promise.reject('两次输入的密码不一致')
        }
        return Promise.resolve()
      },
      trigger: 'blur'
    }
  ],
  agreement: [
    {
      validator: (_rule: any, value: boolean) => {
        if (!value) {
          return Promise.reject('请阅读并同意服务条款和隐私政策')
        }
        return Promise.resolve()
      },
      trigger: 'change'
    }
  ]
}

const handleSubmit = async () => {
  if (!formData.agreement) {
    message.error('请阅读并同意服务条款和隐私政策')
    return
  }

  try {
    loading.value = true
    
    const registerData: RegisterForm = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
      firstName: formData.firstName || undefined,
      lastName: formData.lastName || undefined
    }

    await authStore.register(registerData)
    
    message.success('注册成功！欢迎使用 daloRADIUS')
    
    // 注册成功后跳转到仪表板
    router.push('/dashboard')
    
  } catch (error: any) {
    console.error('Registration failed:', error)
    
    const errorMessage = error?.response?.data?.detail || 
                        error?.message || 
                        '注册失败，请检查输入信息'
    
    message.error(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-form-container {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(50, 50, 93, 0.1), 0 5px 15px rgba(0, 0, 0, 0.07);
  width: 100%;
  max-width: 500px;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-header h1 {
  color: #1890ff;
  margin-bottom: 8px;
  font-size: 28px;
  font-weight: 600;
}

.register-header p {
  color: #8c8c8c;
  font-size: 16px;
  margin: 0;
}

.register-form {
  width: 100%;
}

.register-links {
  text-align: center;
  margin-top: 16px;
}

.register-links a {
  color: #1890ff;
  text-decoration: none;
}

.register-links a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .register-form-container {
    padding: 24px;
    margin: 0 16px;
  }
  
  .register-header h1 {
    font-size: 24px;
  }
}
</style>