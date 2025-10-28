<template>
  <div v-if="showCurtain" class="preloader-overlay" :class="{ 'curtain-closed': isCurtainClosed }">
    <div class="curtain-panel left-curtain">
      <div class="logo-container">
        <div class="logo-text">
          <span class="text-outline">TripTrack</span>
          <span 
            class="text-fill" 
            :style="{ width: textFillWidth }"
          >TripTrack</span>
        </div>
      </div>
    </div>
    <div class="curtain-panel right-curtain">
      <div class="percentage-container">
        <div class="percentage">{{ progress }}%</div>
        <div class="loading-animation">
          <span class="loading-dot" v-for="n in 3" :key="n" :style="getDotStyle(n)"></span>
        </div>
        <div class="loading-text">Loading</div>
      </div>
    </div>
    <!-- Звездный фон -->
    <div class="stars-background"></div>
    <div class="stars-background stars-layer-2"></div>
    <div class="stars-background stars-layer-3"></div>
  </div>
</template>

<script>
/* eslint-disable vue/multi-word-component-names */
export default {
  name: 'Preloader',
  props: {
    progress: {
      type: Number,
      default: 0
    },
    isCurtainClosed: {
      type: Boolean,
      default: false
    },
    showCurtain: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    textFillWidth() {
      return `${this.progress}%`;
    }
  },
  methods: {
    getDotStyle(index) {
      return {
        animationDelay: `${(index - 1) * 0.2}s`
      };
    }
  }
}
</script>

<style scoped>
.preloader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  pointer-events: none;
}

.curtain-panel {
  position: relative;
  width: 50%;
  height: 100%;
  transition: transform 0.6s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* Левая шторка с логотипом */
.left-curtain {
  transform: translateX(-100%);
}

/* Правая шторка с процентами */
.right-curtain {
  transform: translateX(100%);
}

.curtain-closed .left-curtain {
  transform: translateX(0);
}

.curtain-closed .right-curtain {
  transform: translateX(0);
}

/* Улучшенный звездный фон с несколькими слоями */
.stars-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #0a0a2a;
  z-index: -1;
}

.stars-background::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    /* Большие звезды */
    radial-gradient(3px 3px at 5% 10%, #fff, transparent),
    radial-gradient(3px 3px at 15% 25%, #eee, transparent),
    radial-gradient(2px 2px at 25% 40%, #fff, transparent),
    radial-gradient(3px 3px at 35% 15%, #eee, transparent),
    radial-gradient(2px 2px at 45% 60%, #fff, transparent),
    radial-gradient(3px 3px at 55% 30%, #eee, transparent),
    radial-gradient(2px 2px at 65% 75%, #fff, transparent),
    radial-gradient(3px 3px at 75% 45%, #eee, transparent),
    radial-gradient(2px 2px at 85% 20%, #fff, transparent),
    radial-gradient(3px 3px at 95% 55%, #eee, transparent),
    radial-gradient(2px 2px at 10% 80%, #fff, transparent),
    radial-gradient(3px 3px at 30% 90%, #eee, transparent),
    radial-gradient(2px 2px at 50% 85%, #fff, transparent),
    radial-gradient(3px 3px at 70% 95%, #eee, transparent),
    radial-gradient(2px 2px at 90% 70%, #fff, transparent),
    
    /* Средние звезды */
    radial-gradient(2px 2px at 8% 35%, #fff, transparent),
    radial-gradient(2px 2px at 22% 18%, #eee, transparent),
    radial-gradient(1px 1px at 38% 52%, #fff, transparent),
    radial-gradient(2px 2px at 42% 28%, #eee, transparent),
    radial-gradient(1px 1px at 58% 65%, #fff, transparent),
    radial-gradient(2px 2px at 62% 38%, #eee, transparent),
    radial-gradient(1px 1px at 78% 82%, #fff, transparent),
    radial-gradient(2px 2px at 82% 48%, #eee, transparent),
    radial-gradient(1px 1px at 18% 68%, #fff, transparent),
    radial-gradient(2px 2px at 28% 12%, #eee, transparent),
    
    /* Мелкие звезды */
    radial-gradient(1px 1px at 12% 45%, #fff, transparent),
    radial-gradient(1px 1px at 32% 22%, #eee, transparent),
    radial-gradient(1px 1px at 48% 58%, #fff, transparent),
    radial-gradient(1px 1px at 52% 32%, #eee, transparent),
    radial-gradient(1px 1px at 68% 72%, #fff, transparent),
    radial-gradient(1px 1px at 72% 42%, #eee, transparent),
    radial-gradient(1px 1px at 88% 88%, #fff, transparent),
    radial-gradient(1px 1px at 92% 52%, #eee, transparent),
    radial-gradient(1px 1px at 7% 15%, #fff, transparent),
    radial-gradient(1px 1px at 17% 78%, #eee, transparent);
  animation: twinkle 4s ease-in-out infinite alternate;
}

.stars-layer-2::before {
  animation: twinkle 3s ease-in-out infinite alternate-reverse;
  opacity: 0.7;
}

.stars-layer-3::before {
  animation: twinkle 5s ease-in-out infinite alternate;
  opacity: 0.5;
}

@keyframes twinkle {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 1;
  }
}

/* Стили для текстового логотипа */
.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  position: relative;
  font-size: 48px;
  font-weight: bold;
  font-family: 'Arial', sans-serif;
  text-transform: uppercase;
  letter-spacing: 4px;
}

.text-outline {
  color: transparent;
  -webkit-text-stroke: 2px rgba(255, 255, 255, 0.3);
  text-stroke: 2px rgba(255, 255, 255, 0.3);
}

.text-fill {
  position: absolute;
  top: 0;
  left: 0;
  color: #4a90e2;
  background: linear-gradient(90deg, #4a90e2, #67b26f);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  width: 0%;
  overflow: hidden;
  white-space: nowrap;
  transition: width 0.3s ease;
  text-shadow: 0 0 10px rgba(74, 144, 226, 0.5);
  animation: text-glow 2s ease-in-out infinite alternate;
}

@keyframes text-glow {
  from {
    filter: drop-shadow(0 0 5px rgba(74, 144, 226, 0.5));
  }
  to {
    filter: drop-shadow(0 0 15px rgba(74, 144, 226, 0.8));
  }
}

/* Улучшенные стили для процентов и загрузки */
.percentage-container {
  text-align: center;
  color: white;
}

.percentage {
  font-size: 52px;
  font-weight: bold;
  margin-bottom: 15px;
  text-shadow: 0 0 15px rgba(100, 150, 255, 0.9);
  font-family: 'Arial', sans-serif;
  background: linear-gradient(45deg, #4a90e2, #67b26f);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.loading-text {
  font-size: 20px;
  margin-top: 20px;
  text-transform: uppercase;
  letter-spacing: 3px;
  font-family: 'Arial', sans-serif;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 0 10px rgba(100, 150, 255, 0.7);
}

/* Анимация точек загрузки */
.loading-animation {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin: 10px 0;
}

.loading-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(45deg, #4a90e2, #67b26f);
  animation: bounce 1.4s ease-in-out infinite both;
  box-shadow: 0 0 10px rgba(74, 144, 226, 0.7);
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.5);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Блокировка взаимодействия во время загрузки */
.preloader-overlay {
  pointer-events: all;
}
</style>