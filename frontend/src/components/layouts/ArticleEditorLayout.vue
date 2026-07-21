<template>
  <div class="article-editor-layout">
    <!-- 顶部导航栏 -->
    <header class="editor-header">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="Logo" class="logo-img" />
        <h1 class="site-title">Article Editor</h1>
      </div>
      <div class="header-actions">
        <slot name="header-actions"></slot>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="editor-content">
      <slot></slot>
    </main>

    <!-- 页脚 -->
    <footer class="editor-footer">
      <p>© {{ new Date().getFullYear() }} Article Management System</p>
    </footer>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.article-editor-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 2rem;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.logo-img {
  height: 2.5rem;
}

.site-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.editor-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.editor-footer {
  padding: 1rem 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
  border-top: 1px solid #e5e7eb;
}
</style>
