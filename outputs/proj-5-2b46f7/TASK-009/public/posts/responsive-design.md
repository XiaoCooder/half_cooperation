---
title: CSS 响应式设计实战
date: 2025-04-13
tags: [css, design, responsive]
excerpt: 探索现代 CSS 布局技术，构建适配各种设备的界面。
---

# CSS 响应式设计实战

在当今多设备时代，响应式设计已经成为前端开发的必备技能。

## 现代 CSS 布局

### CSS Grid

CSS Grid 是最强大的二维布局系统：

```css
.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}
```

### Flexbox

Flexbox 适合一维布局：

```css
.nav-links {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}
```

## 媒体查询技巧

```css
/* 移动优先 */
.container {
  padding: 1rem;
}

@media (min-width: 768px) {
  .container {
    padding: 2rem;
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

## 容器查询

CSS 容器查询是响应式设计的新范式：

```css
@container (min-width: 400px) {
  .card {
    display: flex;
    flex-direction: row;
  }
}
```

## 动画与交互

使用 CSS 变量实现流畅的动画效果：

```css
:root {
  --transition-duration: 0.3s;
}

.button {
  transition: all var(--transition-duration) ease;
}

.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 255, 0.3);
}
```

## 总结

掌握这些技术可以帮助你构建既美观又实用的响应式界面。