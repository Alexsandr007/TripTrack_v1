<template>
  <div ref="container" class="earth-container">
    <div v-if="loading" class="preloader">
      <div class="preloader-bar" :style="{ width: loadingProgress + '%' }"></div>
      <div class="preloader-text">Загрузка: {{ loadingProgress }}%</div>
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
</template>

<script>
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { onMounted, onUnmounted, ref } from 'vue';

export default {
  name: 'EarthViewer',
  setup() {
    const container = ref(null);
    const loading = ref(true);
    const loadingProgress = ref(0);
    const shouldRotate = ref(true);
    const showPerformance = ref(false);
    const fps = ref(0);
    const memoryUsage = ref(0);
    const triangleCount = ref(0);
    const objectCount = ref(0);
    const gpuInfo = ref('N/A');
    
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

    const cityData = [
      { name: "Москва", lat: 37.3558, lng: 20.6173 },
      { name: "Нью-Йорк", lat: 22.3128, lng: -91.0060 },
      { name: "Токио", lat: 17.1762, lng: 122.6503 },
      { name: "Лондон", lat: 33.0074, lng: -17.1278 },
      { name: "Сидней", lat: -52.3688, lng: 134.2093 }
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
      
      const geometry = new THREE.CircleGeometry(0.02, 32);
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
        currentScale: 1,
        targetScale: 1
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
          const cityInfo = clickedObject.userData;
          alert(`Город: ${cityInfo.name}\nШирота: ${cityInfo.lat}\nДолгота: ${cityInfo.lng}`);
        }
      }
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

      const geometry = new THREE.SphereGeometry(1, 16, 16);

      const manager = new THREE.LoadingManager();
      
      manager.onStart = () => {
        loadingProgress.value = 0;
      };
      
      manager.onProgress = (url, itemsLoaded, itemsTotal) => {
        loadingProgress.value = Math.round((itemsLoaded / itemsTotal) * 100);
      };
      
      manager.onLoad = () => {
        loading.value = false;
        addCitiesToScene();
        animate();
      };

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

      const earthTexture = loadTexture('/5_26KHeightLow.jpg');
      
      const material = new THREE.MeshBasicMaterial({
        map: earthTexture
      });

      earthMesh = new THREE.Mesh(geometry, material);
      scene.add(earthMesh);

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
      for (let i = 0; i < 5000; i++) {
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

    const animate = (timestamp) => {
      animationFrameId = requestAnimationFrame(animate);
      
      const deltaTime = timestamp - lastFrameTime;
      if (deltaTime < frameInterval) return;
      
      lastFrameTime = timestamp - (deltaTime % frameInterval);
      
      if (earthMesh && shouldRotate.value) {
        earthMesh.rotation.y += 0.001;
      }
      
      updateMarkerScales();
      
      if (controls) controls.update();
      if (renderer && scene && camera) renderer.render(scene, camera);
      
      updatePerformanceMetrics();
      renderer.info.reset();
    };

    onMounted(() => {
      initThreeJS();
    });

    onUnmounted(() => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
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
      loading,
      loadingProgress,
      showPerformance,
      fps,
      memoryUsage,
      triangleCount,
      objectCount,
      gpuInfo,
      togglePerformance
    };
  }
};
</script>

<style scoped>
.earth-container {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.preloader {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  max-width: 400px;
  background: rgba(0, 0, 0, 0.7);
  padding: 20px;
  border-radius: 10px;
  color: white;
  text-align: center;
  z-index: 100;
}

.preloader-bar {
  height: 10px;
  background: #4CAF50;
  border-radius: 5px;
  margin-bottom: 10px;
  transition: width 0.3s ease;
}

.preloader-text {
  font-family: Arial, sans-serif;
  font-size: 16px;
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
</style>