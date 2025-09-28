import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

import App from './App.vue'
import router from './router'

// 导入全局样式
import './assets/styles/index.css'

const app = createApp(App)

// 安装插件
app.use(createPinia())
app.use(router)
app.use(Antd)

// 挂载应用
app.mount('#app')
