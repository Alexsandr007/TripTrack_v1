<template>
  <div ref="container" class="three-container"></div>
</template>

<script>
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
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
      const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
      camera.position.z = 50;

      // Рендерер
      const renderer = new THREE.WebGLRenderer();
      renderer.setSize(window.innerWidth, window.innerHeight);
      this.$refs.container.appendChild(renderer.domElement);

        // Освещение
        const pointLight = new THREE.PointLight(0xffffff, 1, 1000, 2);
        pointLight.position.set(100, 200, 100); // Далеко за пределами объекта
        scene.add(pointLight);


        const ambientLight = new THREE.AmbientLight(0xffffff, 1); // Уменьшите интенсивность окружающего света
        scene.add(ambientLight);

      // Post-processing
      const composer = new EffectComposer(renderer);
      const renderPass = new RenderPass(scene, camera);
      composer.addPass(renderPass);
      const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
      composer.addPass(bloomPass);

      // Загрузка модели
      const loader = new GLTFLoader();
      loader.load('/earthNewCard.glb', (gltf) => {
        this.cubes = gltf.scene.children;
        
        // Добавляем имя каждому кубу, если его нет
        
        scene.add(gltf.scene);
      }, undefined, (error) => {
        console.error(error);
      });

      // OrbitControls
      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableZoom = true;
      controls.minDistance = 10;
      controls.maxDistance = 80;

      // Raycasting
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();
      let hoveredCube = null;

      const onMouseMove = (event) => {
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(this.cubes || []);

        if (intersects.length > 0) {
          const intersectedCube = intersects[0].object;
          if (hoveredCube !== intersectedCube) {
            if (hoveredCube) hoveredCube.material.color.set(0xffffff);
            intersectedCube.material.color.set(0xff0000);
            hoveredCube = intersectedCube;
          }
        } else if (hoveredCube) {
          hoveredCube.material.color.set(0xffffff);
          hoveredCube = null;
        }
      };

      const onMouseClick = (event) => {
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(this.cubes || []);

        if (intersects.length > 0) {
          const obj = intersects[0].object;
          
          // Собираем информацию об объекте
          let info = `Информация об объекте:\n\n`;
          info += `Имя: ${obj.name}\n`;
          info += `Тип: ${obj.type}\n`;
          info += `Позиция: x=${obj.position.x.toFixed(2)}, y=${obj.position.y.toFixed(2)}, z=${obj.position.z.toFixed(2)}\n`;
          info += `Вращение: x=${obj.rotation.x.toFixed(2)}, y=${obj.rotation.y.toFixed(2)}, z=${obj.rotation.z.toFixed(2)}\n`;
          info += `Масштаб: x=${obj.scale.x.toFixed(2)}, y=${obj.scale.y.toFixed(2)}, z=${obj.scale.z.toFixed(2)}\n`;
          
          if (obj.material) {
            info += `Материал:\n`;
            info += `  Тип: ${obj.material.type}\n`;
            info += `  Цвет: ${obj.material.color.getHexString()}\n`;
          }
          
          // Добавляем информацию о родительском объекте, если есть
          if (obj.parent) {
            info += `Родительский объект: ${obj.parent.name || obj.parent.type}\n`;
            info += `${Object.keys(obj.material)}\n`;
          }
          
          alert(info);
        }
      };

      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('click', onMouseClick);

      const animate = () => {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
        composer.render();
      };
      animate();

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
  height: 100vh;
}
</style>
