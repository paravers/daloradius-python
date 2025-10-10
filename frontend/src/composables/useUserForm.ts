import { ref, reactive, computed } from 'vue'
import type { User, CreateUserRequest, UpdateUserRequest } from '@/types'
import { userService } from '@/services'

/**
 * 用户表单管理组合式函数
 * 处理用户创建、编辑、查看的表单逻辑
 */
export function useUserForm() {
  // 表单状态
  const visible = ref(false)
  const loading = ref(false)
  const mode = ref<'create' | 'edit' | 'view'>('create')
  const formRef = ref()

  // 表单数据
  const formModel = reactive<Partial<User>>({})
  
  // 原始数据（用于编辑时的对比）
  const originalData = ref<User | null>(null)

  // 计算属性
  const title = computed(() => {
    const titles = {
      create: '添加用户',
      edit: '编辑用户',
      view: '查看用户'
    }
    return titles[mode.value]
  })

  const isReadonly = computed(() => mode.value === 'view')
  const isCreateMode = computed(() => mode.value === 'create')
  const isEditMode = computed(() => mode.value === 'edit')

  const hasChanges = computed(() => {
    if (!originalData.value || isCreateMode.value) return false
    
    // 检查表单数据是否有变化
    const current = formModel
    const original = originalData.value
    
    return (
      current.email !== original.email ||
      current.fullName !== original.fullName ||
      current.status !== original.status ||
      JSON.stringify(current.roles) !== JSON.stringify(original.roles) ||
      current.phoneNumber !== original.phoneNumber
    )
  })

  // 重置表单
  const resetForm = () => {
    Object.keys(formModel).forEach(key => {
      delete formModel[key as keyof typeof formModel]
    })
    formRef.value?.resetFields()
    originalData.value = null
  }

  // 打开创建表单
  const openCreateForm = () => {
    resetForm()
    mode.value = 'create'
    
    // 设置默认值
    Object.assign(formModel, {
      username: '',
      email: '',
      fullName: '',
      password: '',
      roles: ['user'],
      status: 'active'
    })
    
    visible.value = true
  }

  // 打开编辑表单
  const openEditForm = (user: User) => {
    resetForm()
    mode.value = 'edit'
    
    // 复制用户数据到表单
    Object.assign(formModel, {
      id: user.id,
      username: user.username,
      email: user.email,
      fullName: user.fullName,
      roles: [...user.roles],
      status: user.status,
      phoneNumber: user.phoneNumber,
      avatar: user.avatar
    })
    
    // 保存原始数据
    originalData.value = { ...user }
    
    visible.value = true
  }

  // 打开查看表单
  const openViewForm = (user: User) => {
    resetForm()
    mode.value = 'view'
    
    // 复制用户数据到表单
    Object.assign(formModel, user)
    
    visible.value = true
  }

  // 关闭表单
  const closeForm = () => {
    visible.value = false
    setTimeout(resetForm, 200) // 延迟重置，避免关闭动画时表单闪烁
  }

  // 表单验证
  const validateForm = async (): Promise<boolean> => {
    try {
      await formRef.value?.validate()
      return true
    } catch (error) {
      console.warn('表单验证失败:', error)
      return false
    }
  }

  // 创建用户
  const createUser = async (): Promise<User | null> => {
    if (!await validateForm()) return null

    try {
      loading.value = true
      
      const createData: CreateUserRequest = {
        username: formModel.username!,
        email: formModel.email!,
        password: formModel.password!,
        fullName: formModel.fullName,
        roles: formModel.roles || ['user'],
        status: formModel.status || 'active',
        phoneNumber: formModel.phoneNumber,
        sendWelcomeEmail: true
      }

      const newUser = await userService.createUser(createData)
      closeForm()
      return newUser
    } catch (error: any) {
      console.error('创建用户失败:', error)
      throw new Error(error.message || '创建用户失败')
    } finally {
      loading.value = false
    }
  }

  // 更新用户
  const updateUser = async (): Promise<User | null> => {
    if (!formModel.id || !await validateForm()) return null

    try {
      loading.value = true
      
      const updateData: UpdateUserRequest = {
        email: formModel.email,
        fullName: formModel.fullName,
        roles: formModel.roles,
        status: formModel.status,
        phoneNumber: formModel.phoneNumber,
        avatar: formModel.avatar
      }

      const updatedUser = await userService.updateUser(formModel.id, updateData)
      closeForm()
      return updatedUser
    } catch (error: any) {
      console.error('更新用户失败:', error)
      throw new Error(error.message || '更新用户失败')
    } finally {
      loading.value = false
    }
  }

  // 提交表单
  const submitForm = async (): Promise<User | null> => {
    if (isCreateMode.value) {
      return await createUser()
    } else if (isEditMode.value) {
      return await updateUser()
    }
    return null
  }

  // 获取表单字段配置
  const getFormFields = () => {
    return [
      {
        name: 'username',
        type: 'input' as const,
        label: '用户名',
        required: true,
        disabled: isEditMode.value,
        visible: !isViewMode.value || !!formModel.username,
        rules: [
          { required: true, message: '请输入用户名' },
          { min: 3, max: 20, message: '用户名长度在3-20个字符之间' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线' }
        ]
      },
      {
        name: 'email',
        type: 'email' as const,
        label: '邮箱',
        required: true,
        rules: [
          { required: true, message: '请输入邮箱地址' },
          { type: 'email', message: '请输入正确的邮箱格式' }
        ]
      },
      {
        name: 'fullName',
        type: 'input' as const,
        label: '姓名',
        placeholder: '请输入真实姓名'
      },
      {
        name: 'password',
        type: 'password' as const,
        label: '密码',
        required: isCreateMode.value,
        visible: isCreateMode.value,
        rules: [
          { 
            required: isCreateMode.value, 
            message: '请输入密码' 
          },
          { min: 6, message: '密码长度至少6个字符' }
        ]
      },
      {
        name: 'phoneNumber',
        type: 'input' as const,
        label: '手机号',
        placeholder: '请输入手机号码'
      },
      {
        name: 'roles',
        type: 'select' as const,
        label: '角色',
        multiple: true,
        required: true,
        options: [
          { label: '管理员', value: 'admin' },
          { label: '操作员', value: 'operator' },
          { label: '用户', value: 'user' }
        ],
        rules: [
          { required: true, message: '请选择用户角色' }
        ]
      },
      {
        name: 'status',
        type: 'radio' as const,
        label: '状态',
        options: [
          { label: '活跃', value: 'active' },
          { label: '非活跃', value: 'inactive' },
          { label: '已暂停', value: 'suspended' }
        ]
      }
    ]
  }

  // 计算表单是否处于查看模式
  const isViewMode = computed(() => mode.value === 'view')

  return {
    // 状态
    visible,
    loading: loading.value.readonly(),
    mode: mode.value.readonly(),
    formRef,
    formModel,
    
    // 计算属性
    title,
    isReadonly,
    isCreateMode,
    isEditMode,
    isViewMode,
    hasChanges,
    
    // 方法
    openCreateForm,
    openEditForm,
    openViewForm,
    closeForm,
    validateForm,
    submitForm,
    getFormFields,
    resetForm
  }
}