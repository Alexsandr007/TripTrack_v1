<template>
  <div ref="canvasContainer" class="canvas-container"></div>
</template>

<script>
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

export default {
  mounted() {
    this.initThree();
  },
  methods: {
    async initThree() {
      // Создаем сцену
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      const renderer = new THREE.WebGLRenderer({ alpha: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      this.$refs.canvasContainer.appendChild(renderer.domElement);

      // Увеличиваем радиус и количество сегментов сферы
      const radius = 8; // Увеличенный радиус
      const widthSegments = 256; // Увеличенное количество сегментов по ширине
      const heightSegments = 256; // Увеличенное количество сегментов по высоте
      const geometry = new THREE.SphereGeometry(radius, widthSegments, heightSegments);
      const material = new THREE.MeshBasicMaterial({ color: 0x0077ff, wireframe: false });
      const sphere = new THREE.Mesh(geometry, material);
      scene.add(sphere);

      // Загружаем данные из JSON
      const coordinates = await this.loadGeoJSON('/ALLHIGH.geojson');

      this.addLinesFromCoordinates(scene, coordinates, radius); // Передаем радиус

      // Создаем меши для стран
      this.addCountriesFromCoordinates(scene, coordinates, radius); // Добавляем этот вызов

      // Пример вызова функции
      const allMeshes = this.getAllMeshes(scene);
      console.log(allMeshes); // Выводим список всех мешей в консоль

      // Устанавливаем позицию камеры
      camera.position.z = 5; // Увеличиваем расстояние до камеры, чтобы сфера была видна

      // Добавляем OrbitControls для управления вращением
      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true; // Включаем плавное движение
      controls.dampingFactor = 0.25; // Устанавливаем коэффициент затухания
      controls.enableZoom = true; // Включаем возможность зума

      // Инициализация raycaster и вектора мыши
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();

      // Анимация
      // Анимация
      const animate = () => {
        requestAnimationFrame(animate);
        controls.update(); // Обновляем контролы

        // Обновляем raycaster
        mouse.x = (mouse.x / window.innerWidth) * 2 - 1;
        mouse.y = -(mouse.y / window.innerHeight) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);

        // Проверяем пересечения с линиями
        // const intersects = raycaster.intersectObjects(scene.children, true);
        // Убираем выделение линий
        // scene.children.forEach(line => {
        //   if (line instanceof THREE.Line) {
        //     line.material.color.set(0x000000); // Сбрасываем цвет
        //   }
        // });

        // Убираем изменение цвета при наведении
        // intersects.forEach(intersect => {
        //   if (intersect.object instanceof THREE.Line) {
        //     intersect.object.material.color.set(0xff0000); // Меняем цвет на красный
        //   }
        // });

        renderer.render(scene, camera);
      };
      animate();

      // Обработка изменения размера окна
      window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });

      // Обработка движения мыши
      window.addEventListener('mousemove', (event) => {
        mouse.x = event.clientX;
        mouse.y = event.clientY;
      });
    },
    async loadGeoJSON(url) {
      const response = await fetch(url);
      const data = await response.json();
      const coordinates = [];

      // Извлекаем координаты из GeoJSON
      data.features.forEach(feature => {
        if (feature.geometry.type === 'Polygon') {
          coordinates.push(feature.geometry.coordinates[0]); // Добавляем только первый полигон
        } else if (feature.geometry.type === 'MultiPolygon') {
          feature.geometry.coordinates.forEach(polygon => {
            coordinates.push(polygon[0]); // Добавляем первый полигон из каждого MultiPolygon
          });
        }
      });

      return coordinates;
    },
    addLinesFromCoordinates(scene, coordinates, radius) {
      const lineMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });

      coordinates.forEach((polygonCoords) => {
        const points = polygonCoords.map(coord => {
          const longitude = coord[0] * (Math.PI / 180);
          const latitude = coord[1] * (Math.PI / 180);
          const x = radius * Math.cos(latitude) * Math.sin(longitude);
          const y = radius * Math.sin(latitude);
          const z = radius * Math.cos(latitude) * Math.cos(longitude);
          return new THREE.Vector3(x, y, z);
        });

        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const line = new THREE.Line(geometry, lineMaterial);
        scene.add(line);
      });
    },
    addCountriesFromCoordinates(scene, coordinates, radius) {
      const countriesGroup = new THREE.Group(); // Создаем группу для стран
      scene.add(countriesGroup); // Добавляем группу в сцену

      coordinates.forEach((polygonCoords) => {
        const points = polygonCoords.map(coord => {
          const longitude = coord[0] * (Math.PI / 180);
          const latitude = coord[1] * (Math.PI / 180);
          const x = radius * Math.cos(latitude) * Math.sin(longitude);
          const y = radius * Math.sin(latitude);
          const z = radius * Math.cos(latitude) * Math.cos(longitude);
          return new THREE.Vector3(x, y, z);
        });

        // Создаем меш для страны
        const countryGeometry = new THREE.BufferGeometry().setFromPoints(points);
        const countryMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00, side: THREE.DoubleSide });
        const countryMesh = new THREE.Mesh(countryGeometry, countryMaterial);

        countriesGroup.add(countryMesh); // Добавляем меш страны в группу
      });
    },
    getAllMeshes(scene) {
      const meshes = []; // Массив для хранения всех мешей

      scene.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          meshes.push(object); // Добавляем меш в массив
        }
      });

      return meshes; // Возвращаем массив мешей
    }
  }
};
</script>

<style>
.canvas-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>