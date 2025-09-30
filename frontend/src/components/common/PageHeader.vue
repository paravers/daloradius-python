&lt;template&gt;
  &lt;div class="page-header"&gt;
    &lt;div class="page-header__content"&gt;
      &lt;h1 v-if="title" class="page-header__title"&gt;{{ title }}&lt;/h1&gt;
      &lt;p v-if="subtitle" class="page-header__subtitle"&gt;{{ subtitle }}&lt;/p&gt;
    &lt;/div&gt;
    &lt;div v-if="$slots.actions" class="page-header__actions"&gt;
      &lt;slot name="actions" /&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/template&gt;

&lt;script setup lang="ts"&gt;
interface Props {
  title?: string
  subtitle?: string
}

defineProps&lt;Props&gt;()
&lt;/script&gt;

&lt;style scoped&gt;
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.page-header__content {
  flex: 1;
}

.page-header__title {
  font-size: 1.875rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.page-header__subtitle {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
}

.page-header__actions {
  flex-shrink: 0;
  margin-left: 1rem;
}
&lt;/style&gt;