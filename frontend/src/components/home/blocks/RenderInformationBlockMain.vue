<template>

  <div class="information-block">
    <div class="content">
      <div class="card-continent-block">
        <div class="circle-icon">
          <img src="../../../assets/img/home/Africa_Icon.png">
        </div>
        <h2>Africa</h2>
        <p>It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.</p>
      </div>
      <div class="card-continent-block">
        <div class="circle-icon">
          <img src="../../../assets/img/home/America_Icon.png">
        </div>
        <h2>North America</h2>
        <p>It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.</p>
      
      </div>
      <div class="card-continent-block">
        <div class="circle-icon">
          <img src="../../../assets/img/home/Antarctica_Icon.png">
        </div>
        <h2>Antarctica</h2>
        <p>It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.</p>
      
      </div>
      <div class="card-continent-block">
        <div class="circle-icon">
          <img src="../../../assets/img/home/Asia_Icon.png">
        </div>
        <h2>Asia</h2>
        <p>It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.</p>
      
      </div>
      <div class="card-continent-block">
        <div class="circle-icon">
          <img src="../../../assets/img/home/Europe_Icon.png">
        </div>
        <h2>Europe</h2>
        <p>It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.</p>
      
      </div>
      <div class="card-continent-block">
        <div class="circle-icon">
          <img src="../../../assets/img/home/Oceania_Icon.png">
        </div>
        <h2>Australia</h2>
        <p>It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.</p>
      
      </div>
      <div class="card-continent-block">
        <div class="circle-icon">
          <img src="../../../assets/img/home/South_America_Icon.png">
        </div>
        <h2>South America</h2>
        <p>It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.</p>
      
      </div>

    </div>
      <div class="carousel-section" v-if="showCarousel">
        <CarouselComponent 
          :items="carouselItems"
          :drag-threshold="80"
          :auto-play="false"
          @slide-change="onCarouselSlideChange"
        />
      </div>
    </div>



    
</template>
<script>
import { ref } from 'vue'
import VanillaTilt from 'vanilla-tilt';
import CarouselComponent from './CarouselComponent.vue';

export default {
  name: 'RenderInformationBlockMain',
  mounted() {
    this.initTilt();
  },
  components: {
    CarouselComponent // Регистрируем компонент
  },
  methods: {
    initTilt() {
      VanillaTilt.init(document.querySelectorAll(".card-continent-block"), {
        max: 10,
        speed: 400,
        glare: true,
        "max-glare": 0.2,
        scale: 1.05
      });
    },
  },
  setup() {
    const showCarousel = ref(true); // Управление видимостью карусели
    // Данные для слайдов
        const carouselItems = ref([
      {
        image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
        title: 'Горный пейзаж',
        description: 'Величественные горные вершины'
      },
      {
        image: 'https://images.unsplash.com/photo-1518837695005-2083093ee35b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
        title: 'Океанский закат',
        description: 'Закат над бескрайним океаном'
      },
      {
        image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
        title: 'Лесная сказка',
        description: 'Тайны зеленого леса'
      },
      {
        image: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
        title: 'Туманное утро',
        description: 'Рассвет в горах'
      },
      {
        image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
        title: 'Лесная сказка',
        description: 'Тайны зеленого леса'
      },
      {
        image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
        title: 'Лесная сказка',
        description: 'Тайны зеленого леса'
      }])

    return {
      carouselItems,
      showCarousel
    }
  }
}
</script>
<style>


@font-face {
    font-family: "Manrope";
    src: url("../../../assets/fonts/Manrope.ttf");
}

body{
      font-family: "Manrope";
}

/* Стили для карусели */
.carousel-section {
  position: relative;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 1200px;
  z-index: 10;
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 20px;
}

.control-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1000;
}

.toggle-carousel {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.toggle-carousel:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .carousel-section {
    width: 90%;
    bottom: 10px;
    padding: 15px;
  }
  
  .control-panel {
    top: 10px;
    right: 10px;
  }
}

.information-block{
    width: 100%;
    height: auto;
      background: linear-gradient(
    to right, 
    #020C2B 0%, 
    #25438B 50%, 
    #030516 100%
  );
}

.content{
    width: 90%;
    display: flex;
    flex-wrap: wrap;
    gap: 100px 30px;
    justify-content: center;
    padding: 200px 0px 200px 5%;
}

.card-continent-block{
    position: relative;
    width: 300px;
    height: 400px;
    background: #ffffff21;
    padding: 50px 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
    border-radius: 50px;
    transform-style: preserve-3d;

}

.card-continent-block:hover{
    background: #ffffff52;

}

.circle-icon{
    position: absolute;
    display: flex
;
    align-items: center;
    justify-content: center;
    top: -80px;
    background: #fff;
    padding: 20px;
    border-radius: 50%;
}

.circle-icon img{
      width: 100px;
}


.card-continent-block h2{
    color: #fff;

}

.card-continent-block p{
    color: #ffffff;

}

/* Стили для CarouselComponent */
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
  width: 100%;
  height: 400px;
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
  width: 250px;
  height: 350px;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
  transition: transform 0.5s ease, opacity 0.5s ease, filter 0.5s ease;
  filter: brightness(0.8);
  left: 50%;
  top: 50%;
  margin-left: -125px;
  margin-top: -175px;
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
    height: 300px;
  }
  
  .carousel-item {
    width: 200px;
    height: 280px;
    margin-left: -100px;
    margin-top: -140px;
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



</style>