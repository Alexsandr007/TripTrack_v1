<template>
  <div>
    <!-- Прелоадер -->
    <div v-if="isLoading" class="preloader-overlay">
      <div class="preloader-content">
        <div class="preloader-spinner"></div>
        <div class="preloader-text">Загрузка земного шара...</div>
      </div>
    </div>
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
      <button class="toggle-performance" @click="togglePerformance">
        {{ showPerformance ? 'Hide Stats' : 'Show Stats' }}
      </button>
    </div>
  </div>
</template>

<script>
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { onMounted, onUnmounted, ref } from 'vue';

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

    const cityData = [
      { 
        name: "Москва", 
        lat: 37.3558, 
        lng: 20.6173,
        image: "/moscow.jpg",
        description: "Столица России, крупнейший город страны с богатой историей и культурой."
      },
      { 
        name: "Нью-Йорк", 
        lat: 22.3128, 
        lng: -91.0060,
        image: "/new-york.jpg",
        description: "Крупнейший город США, известный своими небоскребами и Статуей Свободы."
      },
      { 
        name: "Токио", 
        lat: 17.1762, 
        lng: 122.6503,
        image: "/tokyo.jpg",
        description: "Столица Японии, современный мегаполис с уникальным сочетанием традиций и технологий."
      },
      { 
        name: "Лондон", 
        lat: 33.0074, 
        lng: -17.1278,
        image: "/london.jpg",
        description: "Столица Великобритании, город с многовековой историей и королевскими достопримечательностями."
      },
      { 
        name: "Сидней", 
        lat: -52.3688, 
        lng: 134.2093,
        image: "/sydney.jpg",
        description: "Крупнейший город Австралии, известный своим оперным театром и мостом Харбор-Бридж."
      }
    ];

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
      
      const geometry = new THREE.CircleGeometry(0.02, 16);
      const material = new THREE.MeshBasicMaterial({ 
        color: 0xffffff,
        transparent: true,
        opacity: 0.8,
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
        0.1,
        1000
      );
      camera.position.z = 2;

      renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        powerPreference: "high-performance"
      });
      renderer.setSize(container.value.clientWidth, container.value.clientHeight);
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
          undefined,
          undefined,
          (error) => {
            console.error('Ошибка загрузки текстуры:', error);
          }
        );
      };

      const earthTexture = loadTexture('/5_26KHeight.webp');
      
      const material = new THREE.MeshBasicMaterial({
        map: earthTexture
      });

      earthMesh = new THREE.Mesh(geometry, material);
      scene.add(earthMesh);

      
      manager.onLoad = () => {
        addCitiesToScene();
        isLoading.value = false; // Скрываем прелоадер когда загрузка завершена
        animate();
      };

      controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.01;

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
      scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight.position.set(1, 1, 1).normalize();
      scene.add(directionalLight);

      const starGeometry = new THREE.BufferGeometry();
      const starMaterial = new THREE.PointsMaterial({
        color: 0xffffff,
        size: 0.02
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
      isLoading
    };
  }
};
</script>

<style scoped>
/* Стили прелоадера */
.preloader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.preloader-content {
  text-align: center;
  color: white;
}

.preloader-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #6a0dad;
  animation: spin 1s ease-in-out infinite;
  margin: 0 auto 20px;
}

.preloader-text {
  font-size: 1.2em;
  margin-top: 15px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.earth-container {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.city-card {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 400px;
  height:600px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  z-index: 100;
  animation: fadeIn 0.3s ease-in-out;
  cursor: default;
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
  color: #ddd;
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
  background-color: #6a0dad; /* Основной фиолетовый цвет */
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.3s ease;
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
</style>