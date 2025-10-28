<template>
  <div>
    <div ref="container" class="earth-container" v-show="!isLoading">
      <div class="city-card" 
      v-if="selectedCity"
      @mouseleave="shouldRotate = true">
    <div class="city-image">
        <img :src="selectedCity.image" :alt="selectedCity.name">
      </div>
      <div class="city-info">
        <h3>{{ selectedCity.name }}</h3>
        <p><strong>Широта:</strong> {{ selectedCity.lat }}</p>
        <p><strong>Долгота:</strong> {{ selectedCity.lng }}</p>
        <p class="city-description">{{ selectedCity.description }}</p>
        
        <!-- Добавленная кнопка -->
        <button class="visit-button" @click="visitCityPage(selectedCity)">
          Перейти на страницу
        </button>
      </div>
      <button class="close-card" @click="selectedCity = null">×</button>
    </div>
      
      <div class="performance-panel" v-if="showPerformance">
        <div>FPS: {{ fps }}</div>
        <div>Memory: {{ memoryUsage }} MB</div>
        <div>Triangles: {{ triangleCount }}</div>
        <div>Objects: {{ objectCount }}</div>
        <div>GPU: {{ gpuInfo }}</div>
      </div>
      <!-- <button class="toggle-performance" @click="togglePerformance">
        {{ showPerformance ? 'Hide Stats' : 'Show Stats' }}
      </button> -->
    </div>
  </div>
</template>

<script>
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { onMounted, onUnmounted, ref } from 'vue';
import { cityData } from '../../../data/cities.js'; // или импортируйте ваши данные о городах

export default {
  name: 'EarthViewer',
  setup() {
    const container = ref(null);
    const shouldRotate = ref(true);
    const isManualRotation = ref(false); // Флаг для ручного вращения
    const showPerformance = ref(false);
    const selectedCity = ref(null);
    const fps = ref(0);
    const memoryUsage = ref(0);
    const triangleCount = ref(0);
    const objectCount = ref(0);
    const gpuInfo = ref('N/A');
    const isLoading = ref(true);
    const fillProgress = ref(0);
    
    let scene, camera, renderer, earthMesh, controls;
    let raycaster, mouse;
    let checkTimeout;
    let cities = [];
    let hoveredCity = null;
    let animationFrameId;
    let resizeObserver;
    let lastFpsUpdate = 0;
    let frames = 0;
    let perfMonitorInterval;
    let lastFrameTime = 0;
    const targetFPS = 60;
    const frameInterval = 1000 / targetFPS;
    let rotationAnimationId = null;

    const togglePerformance = () => {
      showPerformance.value = !showPerformance.value;
      if (showPerformance.value) {
        startPerformanceMonitoring();
      } else {
        stopPerformanceMonitoring();
      }
    };

    const startPerformanceMonitoring = () => {
      perfMonitorInterval = setInterval(() => {
        // Основные метрики теперь обновляются в animate()
      }, 3000);
    };

    const stopPerformanceMonitoring = () => {
      clearInterval(perfMonitorInterval);
    };

    const updatePerformanceMetrics = () => {
      const now = performance.now();
      frames++;
      
      if (now - lastFpsUpdate >= 1000) {
        fps.value = frames;
        frames = 0;
        lastFpsUpdate = now;
        
        if (window.performance?.memory) {
          memoryUsage.value = Math.round(window.performance.memory.usedJSHeapSize / 1048576);
        }
        
        if (scene) {
          let triangles = 0;
          let objects = 0;
          scene.traverse((object) => {
            if (object.isMesh) {
              const geometry = object.geometry;
              triangles += geometry.index ? geometry.index.count / 3 : geometry.attributes.position.count / 3;
              objects++;
            }
          });
          triangleCount.value = triangles;
          objectCount.value = objects;
        }
        
        if (renderer) {
          const gl = renderer.getContext();
          const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
          gpuInfo.value = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'N/A';
        }
      }
    };

    const latLngToVector3 = (lat, lng, radius) => {
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (lng + 180) * (Math.PI / 180);
      
      return new THREE.Vector3(
        -radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.cos(phi),
        radius * Math.sin(phi) * Math.sin(theta)
      );
    };

    const createCityMarker = (city) => {
      const radius = 1.0;
      const position = latLngToVector3(city.lat, city.lng, radius);
      
      const geometry = new THREE.CircleGeometry(0.02, 32);
      const material = new THREE.MeshBasicMaterial({ 
        color: 0xffffff,
        transparent: true,
        opacity: 1,
        side: THREE.DoubleSide
      });
      
      const marker = new THREE.Mesh(geometry, material);
      marker.position.copy(position);
      
      const normal = position.clone().normalize();
      marker.quaternion.setFromUnitVectors(
        new THREE.Vector3(0, 0, 1),
        normal
      );
      marker.rotateZ(Math.PI / 2);
      
      marker.userData = {
        type: 'city',
        name: city.name,
        lat: city.lat,
        lng: city.lng,
        image: city.image,
        description: city.description,
        currentScale: 1,
        targetScale: 1,
        position: position
      };
      
      return marker;
    };

    const addCitiesToScene = () => {
      cityData.forEach(city => {
        const marker = createCityMarker(city);
        earthMesh.add(marker);
        cities.push(marker);
      });
    };

    const closeCityCard = () => {
      selectedCity.value = null;
      shouldRotate.value = true;
      isManualRotation.value = false;
    };

    const rotateToCity = () => {
      if (!earthMesh) return;
      
      shouldRotate.value = false;
      isManualRotation.value = false;
      
      // Отменяем предыдущую анимацию, если она была
      if (rotationAnimationId) {
        cancelAnimationFrame(rotationAnimationId);
      }
      
      const startAngle = earthMesh.rotation.y;
      const targetAngle = startAngle + Math.PI * 2; // 360 градусов в радианах
      const startTime = performance.now();
      const duration = 3000; // 3 секунды анимации для полного оборота
      
      const animateRotation = () => {
        const now = performance.now();
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Плавное замедление в конце
        const easing = (t) => t<.5 ? 2*t*t : -1+(4-2*t)*t;
        
        earthMesh.rotation.y = startAngle + (targetAngle - startAngle) * easing(progress);
        
        if (progress < 1) {
          rotationAnimationId = requestAnimationFrame(animateRotation);
        } else {
          rotationAnimationId = null;
          // После завершения анимации не возобновляем вращение
          shouldRotate.value = false;
        }
      };
      
      rotationAnimationId = requestAnimationFrame(animateRotation);
    };

    const handleCityHover = (cityMarker) => {
      if (hoveredCity === cityMarker) return;
      
      if (hoveredCity) {
        hoveredCity.userData.targetScale = 1;
      }
      
      if (cityMarker) {
        cityMarker.userData.targetScale = 1.5;
        shouldRotate.value = false;
      } else {
        shouldRotate.value = true;
      }
      
      hoveredCity = cityMarker;
    };

    const updateMarkerScales = () => {
      cities.forEach(marker => {
        marker.userData.currentScale = THREE.MathUtils.lerp(
          marker.userData.currentScale,
          marker.userData.targetScale,
          0.1
        );
        
        const scale = marker.userData.currentScale;
        marker.scale.set(scale, scale, scale);
      });
    };

    const handleMouseMove = (event) => {
      clearTimeout(checkTimeout);
      checkTimeout = setTimeout(() => {
        if (!renderer || !camera) return;
        
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects([earthMesh, ...cities], true);
        
        if (intersects.length > 0) {
          const intersectedObject = intersects[0].object;
          
          if (intersectedObject.userData?.type === 'city') {
            handleCityHover(intersectedObject);
          } else if (intersectedObject === earthMesh) {
            handleCityHover(null);
            shouldRotate.value = false;
          }
        } else {
          handleCityHover(null);
          shouldRotate.value = true;
        }
      }, 50);
    };

    const handleClick = (event) => {
      if (!renderer || !camera || !earthMesh) return;
      
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(cities, true);
      
      if (intersects.length > 0) {
        const clickedObject = intersects[0].object;
        
        if (clickedObject.userData.type === 'city') {
          selectedCity.value = clickedObject.userData;
          rotateToCity(selectedCity.value);
        }
      }
    };

    const updateScene = () => {
      if (earthMesh && shouldRotate.value && !rotationAnimationId && !isManualRotation.value) {
        earthMesh.rotation.y += 0.001;
      }
      updateMarkerScales();
      if (controls) controls.update();
    };

    const mouseOutHandler = () => {
      handleCityHover(null);
      shouldRotate.value = true;
    };

    const handleResize = () => {
      if (!camera || !renderer) return;
      
      camera.aspect = container.value.clientWidth / container.value.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.value.clientWidth, container.value.clientHeight);
    };

    const initThreeJS = () => {
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(
        75,
        container.value.clientWidth / container.value.clientHeight,
        0.01,
        1000
      );
      camera.position.z = 2;

      renderer = new THREE.WebGLRenderer({ 
        antialias: true,
      });
      renderer.setSize(container.value.clientWidth, container.value.clientHeight);
      renderer.setClearColor(0x000000, 0); // прозрачный фон

      
      container.value.appendChild(renderer.domElement);

      raycaster = new THREE.Raycaster();
      mouse = new THREE.Vector2();

      renderer.domElement.addEventListener('mousemove', handleMouseMove);
      renderer.domElement.addEventListener('mouseout', mouseOutHandler);
      renderer.domElement.addEventListener('click', handleClick);

      resizeObserver = new ResizeObserver(() => {
        handleResize();
      });
      resizeObserver.observe(container.value);

      const geometry = new THREE.SphereGeometry(1, 64, 64);

      const manager = new THREE.LoadingManager();

      const textureLoader = new THREE.TextureLoader(manager);

      const loadTexture = (url) => {
        return textureLoader.load(
          url,
          (texture) => {
            console.log('Текстура загружена:', texture);
            // Важные настройки текстуры
            texture.colorSpace = THREE.SRGBColorSpace;
            texture.encoding = THREE.sRGBEncoding;
          },
          undefined,
          (error) => {
            console.error('Ошибка загрузки текстуры:', error);
          }
        );
      };

      const earthTexture = loadTexture('/5_26KHeight.webp');
      
      // АЛЬТЕРНАТИВНЫЙ ВАРИАНТ 1: MeshStandardMaterial с правильными настройками
      const material = new THREE.MeshStandardMaterial({
        map: earthTexture,
        side: THREE.DoubleSide,
        metalness: 0,
        roughness: 1,
        toneMapped: false
      });

      earthMesh = new THREE.Mesh(geometry, material);
      scene.add(earthMesh);

      const ambientLight = new THREE.AmbientLight(0xffffff, 3.5); // цвет, интенсивность
      scene.add(ambientLight);

      // Анимация заполнения
      const animateFill = () => {
        if (fillProgress.value < 100) {
          fillProgress.value += 0.5;
          requestAnimationFrame(animateFill);
        }
      };
      
      requestAnimationFrame(animateFill);
      
      manager.onLoad = () => {
        console.log('Все текстуры загружены');
        addCitiesToScene();
        fillProgress.value = 100;
        
        setTimeout(() => {
          isLoading.value = false;
        }, 500);
        animate();
      };

      controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.01;

      // Ключевые настройки для контроля расстояния
      controls.minDistance = 1.3;   // Нельзя приблизиться ближе чем 1.1 единицы
      controls.maxDistance = 5;    // Нельзя отдалиться дальше чем 15 единиц

      const starGeometry = new THREE.BufferGeometry();
      const starMaterial = new THREE.PointsMaterial({
        color: 0xFFFFFF,
        size: 0.05,
        toneMapped: false // Также отключаем для звезд
      });

      const starVertices = [];
      for (let i = 0; i < 20000; i++) {
        const x = (Math.random() - 0.5) * 2000;
        const y = (Math.random() - 0.5) * 2000;
        const z = (Math.random() - 0.5) * 2000;
        starVertices.push(x, y, z);
      }

      starGeometry.setAttribute(
        'position',
        new THREE.Float32BufferAttribute(starVertices, 3)
      );

      const stars = new THREE.Points(starGeometry, starMaterial);
      scene.add(stars);

      renderer.info.autoReset = false;
    };

    const animate = () => {
      if (!renderer || !scene || !camera) return;
      
      animationFrameId = requestAnimationFrame(animate);
      
      // Пропускаем кадры если страница не видима
      if (document.hidden) return;
      
      // Оптимизированный FPS контроль
      const now = performance.now();
      const delta = now - lastFrameTime;
      if (delta < frameInterval) return;
      lastFrameTime = now - (delta % frameInterval);
      
      // Обновление сцены
      updateScene();
      
      renderer.render(scene, camera);
      updatePerformanceMetrics();
    };

    onMounted(() => {
      initThreeJS();
    });

    onUnmounted(() => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      if (rotationAnimationId) cancelAnimationFrame(rotationAnimationId);
      stopPerformanceMonitoring();
      
      if (renderer) {
        renderer.domElement.removeEventListener('mousemove', handleMouseMove);
        renderer.domElement.removeEventListener('mouseout', mouseOutHandler);
        renderer.domElement.removeEventListener('click', handleClick);
        renderer.dispose();
      }
      
      if (resizeObserver) {
        resizeObserver.disconnect();
      }

    });

    return {
      container,
      selectedCity,
      showPerformance,
      fps,
      memoryUsage,
      triangleCount,
      objectCount,
      gpuInfo,
      togglePerformance,
      rotateToCity,
      closeCityCard,
      isLoading,
      fillProgress,
    };
  },
  methods: {
    visitCityPage(city) {
      // Закрываем карточку города
      this.selectedCity = null;
      // Переходим на страницу города
      this.$router.push({
        name: 'CityPage', // имя маршрута из вашего router.js
        params: { 
          cityName: city.name.toLowerCase().replace(/\s+/g, '-') // преобразуем имя города в URL-формат
        }
      });
    }
  }
};
</script>

<style scoped>
/* Стили звездного неба (без изменений) */
.preloader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, #0a0e24 0%, #1a1b3a 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  overflow: hidden;
}

.stars, .stars2, .stars3 {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
}

.stars {
  background-image: radial-gradient(1px 1px at 20px 30px, white, rgba(0,0,0,0));
  background-size: 100px 100px;
  animation: starsAnimation 50s linear infinite;
}

.stars2 {
  background-image: radial-gradient(1px 1px at 40px 70px, white, rgba(0,0,0,0));
  background-size: 150px 150px;
  animation: starsAnimation 100s linear infinite;
}

.stars3 {
  background-image: radial-gradient(1px 1px at 90px 40px, white, rgba(0,0,0,0));
  background-size: 200px 200px;
  animation: starsAnimation 150s linear infinite;
}

@keyframes starsAnimation {
  from { transform: translateY(0); }
  to { transform: translateY(-200px); }
}

/* НОВЫЕ СТИЛИ ДЛЯ АНИМАЦИИ ТЕКСТА */
.preloader-content {
  position: relative;
  z-index: 10;
}

.logo-animation-container {
  position: relative;
  display: inline-block;
}

.logo-text-outline {
  font-size: 5rem;
  font-weight: 800;
  letter-spacing: 5px;
  color: transparent;
  -webkit-text-stroke: 2px rgba(255, 255, 255, 0.3);
}

.logo-text-mask {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  overflow: hidden;
  transition: width 0.5s ease-out;
  white-space: nowrap;
}

.logo-text-filled {
  font-size: 5rem;
  font-weight: 800;
  letter-spacing: 5px;
  background: linear-gradient(to right, #1a3a8f, #0a1a4a);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* Анимация исчезновения */
.preloader-overlay.fade-out {
  animation: fadeOut 0.8s forwards;
}

@keyframes fadeOut {
  to {
    opacity: 0;
    visibility: hidden;
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .logo-text-outline,
  .logo-text-filled {
    font-size: 3rem;
    letter-spacing: 3px;
  }
}

.earth-container {
  width: 100%;
  height: 800px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(
    to right, 
    #020C2B 0%, 
    #25438B 50%, 
    #030516 100%
  );
}

.city-card {
    position: absolute;
    top: 100px;
    right: 20px;
    margin-left: 20px;
    max-width: 400px;
    height: 600px;
    background: rgb(130 130 130 / 23%);
    color: #000000;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    z-index: 100;
    animation: fadeIn-2742af1a 0.3s 
ease-in-out;
    cursor: default;
    backdrop-filter: blur(5px);
}

.city-card:hover {
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
}

.city-image {
  width: 100%;
  height: 180px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 15px;
}

.city-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.city-info h3 {
  margin: 0 0 10px 0;
  font-size: 1.5em;
  color: #fff;
}

.city-info p {
    margin: 5px 0;
    font-size: 0.9em;
    color: #ffffff;
}

.city-description {
  margin-top: 15px !important;
  line-height: 1.5;
}

.close-card {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  color: white;
  font-size: 1.5em;
  cursor: pointer;
  padding: 0 5px;
  line-height: 1;
}

.close-card:hover {
  color: #ccc;
}

.performance-panel {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 10px;
  border-radius: 5px;
  font-family: monospace;
  z-index: 100;
}

.toggle-performance {
  position: absolute;
  bottom: 20px;
  right: 20px;
  padding: 8px 15px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  z-index: 100;
}

.toggle-performance:hover {
  background: rgba(50, 50, 50, 0.7);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.visit-button {
    display: inline-block;
    margin-top: 15px;
    padding: 10px 20px;
    background-color: #011e3f;
    background: linear-gradient(to right, #020C2B -25%, #25438B 50%, #030516 150%);
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 0.9em;
    cursor: pointer;
    transition: all 0.3s 
ease;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.visit-button:hover {
  background-color: #8a2be2; /* Более светлый фиолетовый при наведении */
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.visit-button:active {
  background-color: #4b0082; /* Темный индиго при нажатии */
  transform: translateY(0);
}


* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
    padding: 20px;
    overflow-x: hidden;
}

#app {
    max-width: 1200px;
    width: 100%;
    text-align: center;
    padding: 20px;
}

h1 {
    color: white;
    margin-bottom: 10px;
    font-size: 2.5rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.subtitle {
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 40px;
    font-size: 1.2rem;
}

.carousel-wrapper {
    position: relative;
    width: 100%;
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
}

.carousel-container {
    position: relative;
    width: 100%;
    height: 500px;
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
    width: 280px;
    height: 380px;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    transition: transform 0.5s ease, opacity 0.5s ease, filter 0.5s ease;
    filter: brightness(0.8);
    left: 50%;
    top: 50%;
    margin-left: -140px;
    margin-top: -190px;
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
    padding: 20px;
    text-align: center;
    pointer-events: none;
}

.carousel-caption h3 {
    font-size: 1.5rem;
    margin-bottom: 5px;
}

.carousel-caption p {
    font-size: 1rem;
    opacity: 0.8;
}

.drag-hint {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.9rem;
    background: rgba(0, 0, 0, 0.3);
    padding: 8px 15px;
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
    margin-top: 30px;
    gap: 20px;
}

.btn {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    padding: 12px 20px;
    border-radius: 50px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.btn:active {
    transform: translateY(1px);
}

.indicators {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 20px;
}

.indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    cursor: pointer;
    transition: all 0.3s ease;
}

.indicator.active {
    background: white;
    transform: scale(1.2);
}

@media (max-width: 768px) {
    .carousel-container {
        height: 400px;
    }
    
    .carousel-item {
        width: 220px;
        height: 320px;
        margin-left: -110px;
        margin-top: -160px;
    }
    
    h1 {
        font-size: 2rem;
    }
}

@media (max-width: 480px) {
    .carousel-container {
        height: 350px;
    }
    
    .carousel-item {
        width: 180px;
        height: 260px;
        margin-left: -90px;
        margin-top: -130px;
    }
    
    .controls {
        flex-direction: column;
        gap: 10px;
    }
    
    .drag-hint {
        font-size: 0.8rem;
        padding: 6px 12px;
    }
}
</style>