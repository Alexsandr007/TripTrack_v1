<template>
  <div ref="container" class="three-container"></div>
</template>

<script>
import * as THREE from 'three';
// import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'; // Импортируем OrbitControls
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';

export default {
  name: 'ThreeDModel',
  mounted() {
    this.initThree();
  },
  methods: {
    initThree() {
      // Сцена
      const scene = new THREE.Scene();

      const spaceTexture = new THREE.TextureLoader().load('/space.jpg');
      scene.background = spaceTexture;
      // Камера
      const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      camera.position.z = 1000;

      // Рендерер
      const renderer = new THREE.WebGLRenderer();
      renderer.setSize(window.innerWidth, window.innerHeight);
      this.$refs.container.appendChild(renderer.domElement);

      // Освещение
      const pointLight = new THREE.PointLight(0xffffff, 100, 100); // White point light
      pointLight.position.set(2, 4, 4); // Positioning the point light
      scene.add(pointLight);

      // renderer.setClearColor(0xffffff, 0.6); // Установите белый цвет фона


      const ambientLight = new THREE.AmbientLight(0xffffff, 10); // Белый свет с интенсивностью 0.5
      scene.add(ambientLight);

      // Создайте composer для постобработки
      const composer = new EffectComposer(renderer);
      const renderPass = new RenderPass(scene, camera);
      composer.addPass(renderPass);

      // Добавьте UnrealBloomPass
      const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
      composer.addPass(bloomPass);

      // Загрузка GLB модели
      // const loader = new GLTFLoader();
      // loader.load('/planet_v2.glb', (gltf) => {
      //   scene.add(gltf.scene);
      // }, undefined, (error) => {
      //   console.error(error);
      // });

      // Загрузка OBJ модели

      const mtlLoader = new MTLLoader();
      mtlLoader.load('/planet_v4_pract.mtl', (materials) => {
        materials.preload();
        
        // Загрузка OBJ файла
        const objLoader = new OBJLoader();
        objLoader.setMaterials(materials);
        objLoader.load('/planet_v4_pract.obj', (object) => {
          scene.add(object);
        }, undefined, (error) => {
          console.error(error);
        });
      });

      // Добавляем OrbitControls
      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableZoom = true; // Включаем зум
      controls.minDistance = 1; // Минимальное расстояние для зума
      controls.maxDistance = 10; // Максимальное расстояние для зума

      // Анимация
      const animate = () => {
        requestAnimationFrame(animate);
        controls.update(); // Обновляем контроллеры
        renderer.render(scene, camera);
        composer.render();
      };
      animate();
      

      // Обработка изменения размера окна
      window.addEventListener('resize', () => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        renderer.setSize(width, height);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
      });
    },
  },
};
</script>

<style scoped>
.three-container {
  width: 100%;
  height: 100vh; /* Занимает всю высоту окна */
}
</style>