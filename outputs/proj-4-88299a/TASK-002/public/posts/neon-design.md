# 霓虹光效设计美学

深入探讨科幻风格的视觉设计实现技巧。

## 科幻视觉元素

赛博朋克美学融合了复古与未来感，霓虹光效是其标志性元素。

### 核心配色方案

```css
/* 科幻主题配色 */
:root {
  --scifi-bg: #0a0a0f;       /* 深空黑 */
  --scifi-primary: #00d4ff;  /* 青色霓虹 */
  --scifi-secondary: #7000ff; /* 紫色霓虹 */
  --scifi-accent: #ff006e;   /* 粉色霓虹 */
}
```

## 霓虹光效实现

### 文字发光效果

```css
.neon-text {
  text-shadow:
    0 0 5px #00d4ff,
    0 0 10px #00d4ff,
    0 0 20px #00d4ff,
    0 0 40px #00d4ff;
}
```

### 边框发光效果

```css
.neon-border {
  box-shadow:
    inset 0 0 5px rgba(0, 212, 255, 0.2),
    0 0 5px rgba(0, 212, 255, 0.3),
    0 0 10px rgba(0, 212, 255, 0.2);
  border: 1px solid rgba(0, 212, 255, 0.3);
}
```

## 网格背景动画

```css
.grid-background::before {
  background-image:
    linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridMove 20s linear infinite;
}
```

## 扫描线效果

复古 CRT 显示器的扫描线效果：

```css
.scanlines::after {
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.1) 0px,
    rgba(0, 0, 0, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
}
```

## 设计原则

1. **对比度** - 深色背景配合明亮霓虹
2. **动感** - 脉冲、呼吸等微妙动画
3. **层次感** - 多种光效叠加
4. **克制** - 不要过度使用，保持可读性

## 总结

科幻风格设计是技术与艺术的结合，通过 CSS 就能实现大部分效果。记住：设计服务于内容，用户体验始终是第一位。