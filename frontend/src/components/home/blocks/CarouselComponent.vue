<!-- components/CarouselComponent.vue -->
<template>
  <div class="carousel-wrapper">
    <div class="carousel-wrapper-inner">
      <div 
        class="carousel-container"
        :class="{ dragging: isDragging }"
        @mousedown="startDrag"
        @touchstart="startDrag"
      >
        <div 
          class="carousel"
          :class="{ dragging: isDragging }"
        >
          <div
            v-for="(item, index) in items"
            :key="index"
            class="carousel-item"
            :class="{ active: getPositionIndex(index) === 0 }"
            :style="getItemStyle(index)"
          >
            <img :src="item.image" :alt="item.title">
            <div class="carousel-caption">
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </div>
        </div>
        <div v-if="visibleCount > 1" class="drag-hint">← Перетащите влево для предыдущего →</div>
      </div>
    </div>
    
    <div class="controls">
      <button class="btn" @click="prevSlide">
        <span>←</span> Назад
      </button>
      <button class="btn" @click="nextSlide">
        Вперед <span>→</span>
      </button>
    </div>
    
    <div class="indicators">
      <div
        v-for="(item, index) in items"
        :key="index"
        class="indicator"
        :class="{ active: currentIndex === index }"
        @click="goToSlide(index)"
      ></div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';

export default {
  name: 'CarouselComponent',
  props: {
    items: {
      type: Array,
      required: true,
      default: () => []
    },
    dragThreshold: {
      type: Number,
      default: 80
    },
    autoPlay: {
      type: Boolean,
      default: false
    },
    autoPlayInterval: {
      type: Number,
      default: 3000
    }
  },
  emits: ['slide-change'],
  setup(props, { emit }) {
    const currentIndex = ref(0);
    const isDragging = ref(false);
    const startX = ref(0);
    const currentX = ref(0);
    const currentTranslate = ref(0);
    const visibleCount = ref(5);
    let autoPlayTimer = null;
    
    // Обновление количества видимых слайдов на основе ширины экрана
    const updateVisibleCount = () => {
      const width = window.innerWidth;
      if (width <= 768) {
        visibleCount.value = 1;
      } else if (width <= 1024) {
        visibleCount.value = 3;
      } else {
        visibleCount.value = 5;
      }
    };
    
    // Позиции для клиновидной компоновки, зависят от visibleCount
    const wedgePositions = computed(() => {
      if (visibleCount.value === 1) {
        return [
          { z: 100, x: 0, y: 0, scale: 1.0, opacity: 1 }
        ];
      } else if (visibleCount.value === 3) {
        return [
          { z: 100, x: 0, y: 0, scale: 1.0, opacity: 1 },
          { z: 50, x: -180, y: 20, scale: 0.85, opacity: 0.8 },
          { z: 50, x: 180, y: 20, scale: 0.85, opacity: 0.8 }
        ];
      } else {
        return [
          { z: 100, x: 0, y: 0, scale: 1.0, opacity: 1 },
          { z: 50, x: -180, y: 20, scale: 0.85, opacity: 0.8 },
          { z: 50, x: 180, y: 20, scale: 0.85, opacity: 0.8 },
          { z: 0, x: -320, y: 40, scale: 0.7, opacity: 0.6 },
          { z: 0, x: 320, y: 40, scale: 0.7, opacity: 0.6 }
        ];
      }
    });
    
    const totalItems = computed(() => props.items.length);
    
    const getPositionIndex = (itemIndex) => {
      const relativeIndex = (itemIndex - currentIndex.value + totalItems.value) % totalItems.value;
      
      if (visibleCount.value === 1) {
        return relativeIndex === 0 ? 0 : -1;
      } else if (visibleCount.value === 3) {
        if (relativeIndex === 0) return 0;
        if (relativeIndex === 1) return 1;
        if (relativeIndex === totalItems.value - 1) return 2;
        return -1;
      } else {
        // Оригинальная логика для 5 слайдов
        if (relativeIndex === 0) return 0;
        if (relativeIndex === 1) return 1;
        if (relativeIndex === totalItems.value - 1) return 2;
        if (relativeIndex === 2) return 3;
        if (relativeIndex === totalItems.value - 2) return 4;
        return -1;
      }
    };
    
    const getItemStyle = (itemIndex) => {
      const positionIndex = getPositionIndex(itemIndex);
      
      if (positionIndex !== -1 && !isDragging.value) {
        const pos = wedgePositions.value[positionIndex];
        return {
          transform: `translate3d(${pos.x}px, ${pos.y}px, ${pos.z}px) scale(${pos.scale})`,
          opacity: pos.opacity
        };
      } else if (positionIndex !== -1 && isDragging.value) {
        const pos = wedgePositions.value[positionIndex];
        return {
          transform: `translate3d(${pos.x - currentTranslate.value * 0.5}px, ${pos.y}px, ${pos.z}px) scale(${pos.scale})`,
          opacity: pos.opacity
        };
      } else {
        return {
          transform: 'translate3d(0, 0, -500px) scale(0.5)',
          opacity: '0'
        };
      }
    };
    
    const nextSlide = () => {
      currentIndex.value = (currentIndex.value + 1) % totalItems.value;
      emit('slide-change', currentIndex.value);
    };
    
    const prevSlide = () => {
      currentIndex.value = (currentIndex.value - 1 + totalItems.value) % totalItems.value;
      emit('slide-change', currentIndex.value);
    };
    
    const goToSlide = (index) => {
      currentIndex.value = index;
      emit('slide-change', currentIndex.value);
    };
    
    const startDrag = (e) => {
      isDragging.value = true;
      startX.value = getClientX(e);
      currentX.value = startX.value;
      
      document.addEventListener('mousemove', drag);
      document.addEventListener('mouseup', endDrag);
      document.addEventListener('touchmove', drag);
      document.addEventListener('touchend', endDrag);
      
      e.preventDefault();
    };
    
    const drag = (e) => {
      if (!isDragging.value) return;
      
      currentX.value = getClientX(e);
      currentTranslate.value = currentX.value - startX.value;
      
      e.preventDefault();
    };
    
    const endDrag = () => {
      if (!isDragging.value) return;
      
      isDragging.value = false;
      const absDiff = Math.abs(currentTranslate.value);
      
      if (absDiff > props.dragThreshold) {
        if (currentTranslate.value > 0) {
          nextSlide();
        } else {
          prevSlide();
        }
      }
      
      currentTranslate.value = 0;
      
      document.removeEventListener('mousemove', drag);
      document.removeEventListener('mouseup', endDrag);
      document.removeEventListener('touchmove', drag);
      document.removeEventListener('touchend', endDrag);
    };
    
    const getClientX = (e) => {
      return e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
    };
    
    const startAutoPlay = () => {
      if (props.autoPlay) {
        autoPlayTimer = setInterval(nextSlide, props.autoPlayInterval);
      }
    };
    
    const stopAutoPlay = () => {
      if (autoPlayTimer) {
        clearInterval(autoPlayTimer);
        autoPlayTimer = null;
      }
    };
    
    onMounted(() => {
      updateVisibleCount();
      window.addEventListener('resize', updateVisibleCount);
      if (props.autoPlay) {
        startAutoPlay();
      }
    });
    
    onUnmounted(() => {
      window.removeEventListener('resize', updateVisibleCount);
      stopAutoPlay();
    });
    
    return {
      currentIndex,
      isDragging,
      startX,
      currentX,
      currentTranslate,
      visibleCount,
      wedgePositions,
      totalItems,
      getPositionIndex,
      getItemStyle,
      nextSlide,
      prevSlide,
      goToSlide,
      startDrag,
      drag,
      endDrag,
      getClientX
    };
  }
};
</script>

<style scoped>
.carousel-wrapper {
  width: 100%;
  text-align: center;
}

.carousel-wrapper-inner {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.carousel-container {
  position: relative;
  width: 96%; /* Изменено с 100% на 96% для занятия 96% экрана */
  height: 700px; /* Увеличено с 600px для размещения карточек высотой 400px с смещениями */
  perspective: 1500px;
  display: flex;
  justify-content: center;
  cursor: grab;
  user-select: none;
  overflow: hidden;
}

.carousel-container.dragging {
  cursor: grabbing;
}

.carousel {
  position: absolute;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.carousel.dragging {
  transition: none;
}

.carousel-item {
  position: absolute;
  width: 300px; /* Увеличено с 300px (уже было, но высота изменена) */
  height: 400px; /* Увеличено с 390px */
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
  transition: transform 0.5s ease, opacity 0.5s ease, filter 0.5s ease;
  filter: brightness(0.8);
  left: 50%;
  top: 50%;
  margin-left: -150px; /* Скорректировано для центрирования (половина ширины 300px) */
  margin-top: -200px; /* Скорректировано для центрирования (половина высоты 400px) */
  touch-action: pan-y;
}

.carousel-item.active {
  filter: brightness(1);
  z-index: 10;
}

.carousel-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none;
}

.carousel-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  color: white;
  padding: 15px;
  text-align: center;
  pointer-events: none;
}

.carousel-caption h3 {
  font-size: 1.2rem;
  margin-bottom: 5px;
}

.carousel-caption p {
  font-size: 0.9rem;
  opacity: 0.8;
}

.drag-hint {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  background: rgba(0, 0, 0, 0.3);
  padding: 6px 12px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  animation: pulse 2s infinite;
  z-index: 100;
}

@keyframes pulse {
  0% { opacity: 0.7; }
  50% { opacity: 1; }
  100% { opacity: 0.7; }
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 10px 15px;
  border-radius: 50px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.indicators {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 15px;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator.active {
  background: white;
  transform: scale(1.2);
}

/* Адаптивность */
@media (max-width: 768px) {
  .carousel-container {
    height: 700px; /* Увеличено для соответствия */
  }
  
  .carousel-item {
    width: 250px;
    height: 350px;
    margin-left: -125px; /* Скорректировано (половина 250px) */
    margin-top: -175px; /* Скорректировано (половина 350px) */
  }
  
  .carousel-caption {
    padding: 10px;
  }
  
  .carousel-caption h3 {
    font-size: 1rem;
  }
  
  .carousel-caption p {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .carousel-container {
    height: 700px; /* Увеличено для соответствия */
  }
  
  .carousel-item {
    width: 250px;
    height: 350px;
    margin-left: -125px; /* Скорректировано (половина 250px) */
    margin-top: -175px; /* Скорректировано (половина 350px) */
  }
  
  .carousel-caption {
    padding: 8px;
  }
  
  .carousel-caption h3 {
    font-size: 0.9rem;
  }
  
  .carousel-caption p {
    font-size: 0.7rem;
  }
}
</style>