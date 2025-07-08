<template>
  <div ref="container" class="earth-container">
    <div v-if="loading" class="preloader">
      <div class="preloader-bar" :style="{ width: loadingProgress + '%' }"></div>
      <div class="preloader-text">Загрузка: {{ loadingProgress }}%</div>
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
    const loading = ref(true);
    const loadingProgress = ref(0);
    const isHoveringEarth = ref(false); // Добавляем состояние для отслеживания наведения на Землю
    
    let scene, camera, renderer, earthMesh, controls;
    let raycaster, mouse; // Объявляем переменные для Raycaster
    let checkTimeout; // Для троттлинга проверок

    const checkIntersection = (event) => {
      clearTimeout(checkTimeout);
      checkTimeout = setTimeout(() => {
        if (!renderer) return;
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        isHoveringEarth.value = raycaster.intersectObject(earthMesh).length > 0;
      }, 50);
    };

    const mouseOutHandler = () => {
      isHoveringEarth.value = false;
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
      
      renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(container.value.clientWidth, container.value.clientHeight);
      container.value.appendChild(renderer.domElement);

      raycaster = new THREE.Raycaster();
      mouse = new THREE.Vector2();

      renderer.domElement.addEventListener('mousemove', checkIntersection);
      renderer.domElement.addEventListener('mouseout', mouseOutHandler);

      // Создаем сферу
      const geometry = new THREE.SphereGeometry(1, 64, 64);

      // Менеджер загрузки с отслеживанием прогресса
      const manager = new THREE.LoadingManager();
      
      manager.onStart = () => {
        loadingProgress.value = 0;
      };
      
      manager.onProgress = (url, itemsLoaded, itemsTotal) => {
        loadingProgress.value = Math.round((itemsLoaded / itemsTotal) * 100);
      };
      
      manager.onLoad = () => {
        loading.value = false;
        animate();
      };

      const textureLoader = new THREE.TextureLoader(manager);

      // Загрузка текстур с обработкой ошибок
      const loadTexture = (url) => {
        return textureLoader.load(
          url,
          undefined, // onLoad callback не нужен, так как есть manager.onLoad
          undefined, // onProgress callback
          (error) => {
            console.error('Ошибка загрузки текстуры:', error);
          }
        );
      };

      const earthTexture = loadTexture(
        '/5_26KHeight.jpg'
      );
      
      // Остальной код создания материала и меша...
      const material = new THREE.MeshPhongMaterial({
        map: earthTexture,
        shininess: 5
      });

      earthMesh = new THREE.Mesh(geometry, material);
      scene.add(earthMesh);

      // Настройка OrbitControls
      controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.01;

      // 1. Увеличиваем интенсивность ambient (рассеянного) света
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5); // Белый свет, интенсивность 0.5
      scene.add(ambientLight);

      // 2. Добавляем несколько направленных источников света
      // Основной источник (имитация Солнца)
      const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight1.position.set(1, 1, 1).normalize(); // Нормализуем вектор
      scene.add(directionalLight1);

      // Дополнительный источник с противоположной стороны
      const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
      directionalLight2.position.set(-1, -0.5, -1).normalize();
      scene.add(directionalLight2);

      // 3. Добавляем гемисферический свет для мягкого освещения
      const hemisphereLight = new THREE.HemisphereLight(
        0x4488aa, // цвет неба (верхний свет)
        0xcc8866, // цвет земли (нижний свет)
        0.6 // интенсивность
      );
      scene.add(hemisphereLight);
      // Звездный фон
      const starGeometry = new THREE.BufferGeometry();
      const starMaterial = new THREE.PointsMaterial({
        color: 0xffffff,
        size: 0.02
      });

      const starVertices = [];
      for (let i = 0; i < 10000; i++) {
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

    };

    const animate = () => {
      requestAnimationFrame(animate);
      
      if (earthMesh && !isHoveringEarth.value) {
        earthMesh.rotation.y += 0.001;
      }
      
      if (controls) controls.update();
      if (renderer && scene && camera) renderer.render(scene, camera);
    };

    onMounted(() => {
      initThreeJS();
      animate();
    });

    onUnmounted(() => {
      if (renderer) {
        renderer.domElement.removeEventListener('mousemove', checkIntersection);
        renderer.domElement.removeEventListener('mouseout', mouseOutHandler);
        renderer.dispose();
      }
    });

    return {
      container,
      loading,
      loadingProgress,
      // Не возвращаем checkIntersection и mouseOutHandler,
      // так как они используются только внутри компонента
    };
  }
};
</script>

<style scoped>
.earth-container {
  width: 100%;
  height: 100vh;
  position: relative;
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
</style>