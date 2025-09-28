<template>
  <div class="login-container">
    <div class="login-form-container">
      <div class="login-header">
        <h1>daloRADIUS</h1>
        <p>RADIUS 管理系统</p>
      </div>
      
      <a-form
        :model="formData"
        :rules="rules"
        @finish="handleSubmit"
        layout="vertical"
        class="login-form"
      >
        <a-form-item name="username" label="用户名">
          <a-input
            v-model:value="formData.username"
            size="large"
            placeholder="请输入用户名"
            :prefix="h(UserOutlined)"
          />
        </a-form-item>

        <a-form-item name="password" label="密码">
          <a-input-password
            v-model:value="formData.password"
            size="large"
            placeholder="请输入密码"
            :prefix="h(LockOutlined)"
          />
        </a-form-item>

        <a-form-item name="remember">
          <a-checkbox v-model:checked="formData.remember">
            记住我
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
            登录
          </a-button>
        </a-form-item>
      </a-form>

      <div class="login-footer">
        <a-typography-text type="secondary">
          © 2024 daloRADIUS. All rights reserved.
        </a-typography-text>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores'
import type { LoginForm } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(false)

// 表单数据
const formData = reactive<LoginForm>({
  username: '',
  password: '',
  remember: false,
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度为2-50个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度为6-100个字符', trigger: 'blur' },
  ],
}

// 提交登录
const handleSubmit = async (values: LoginForm) => {
  try {
    loading.value = true
    await authStore.login(values)
    
    // 登录成功，跳转到原来的页面或仪表板
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (error: any) {
    console.error('Login error:', error)
    message.error(error.message || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-form-container {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
}

.login-header p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.login-form {
  margin-bottom: 24px;
}

.login-footer {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-form-container {
    padding: 24px;
    margin: 0 16px;
  }
}
</style>