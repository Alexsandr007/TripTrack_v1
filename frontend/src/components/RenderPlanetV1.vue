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
      camera.position.z = 10; // Увеличиваем расстояние до камеры, чтобы сфера была видна

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
      const coordinates = {};

      // Извлекаем координаты из GeoJSON
      data.features.forEach(feature => {
        const name = feature.properties.name; // Получаем имя из свойств
        if (feature.geometry.type === 'Polygon') {
          // Если полигон, добавляем его в массив
          coordinates[name] = coordinates[name] || []; // Инициализируем массив, если он не существует
          coordinates[name].push(feature.geometry.coordinates[0]); // Добавляем полигон в массив
        } else if (feature.geometry.type === 'MultiPolygon') {
          // Если мультиполигон, добавляем все полигоны в массив
          coordinates[name] = coordinates[name] || []; // Инициализируем массив, если он не существует
          feature.geometry.coordinates.forEach(polygon => {
            coordinates[name].push(polygon[0]); // Добавляем первый полигон из каждого MultiPolygon в массив
          });
        }
      });

      console.log(coordinates);
      return coordinates;
    },
    addLinesFromCoordinates(scene, coordinates, radius) {
      const lineMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });

      // Проходим по каждому имени в coordinates
      Object.values(coordinates).forEach(polygons => {
        // Проверяем, является ли polygons массивом
        if (Array.isArray(polygons)) {
          polygons.forEach(polygonCoords => {

            // Проверяем, является ли polygonCoords массивом массивов
            if (Array.isArray(polygonCoords[0])) {
              // Если это массив массивов, проходим по каждому полигону

              const points = polygonCoords.map(coords => {

                const longitude = coords[0] * (Math.PI / 180);
                const latitude = coords[1] * (Math.PI / 180);

                // Проверка на NaN
                if (isNaN(longitude) || isNaN(latitude)) {
                  console.log("TOP");
                  console.error('NaN found in coordinates:', { longitude, latitude });
                }

                const x = radius * Math.cos(latitude) * Math.sin(longitude);
                const y = radius * Math.sin(latitude);
                const z = radius * Math.cos(latitude) * Math.cos(longitude);

                // Проверка на NaN после вычисления
                if (isNaN(x) || isNaN(y) || isNaN(z)) {
                  console.error('NaN found in computed coordinates:', { x, y, z });
                }

                return new THREE.Vector3(x, y, z);
              });

              // Проверка на пустой массив points
              if (points.length > 0) {
                // Создаем линию для каждого полигона
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const line = new THREE.Line(geometry, lineMaterial);
                scene.add(line);
              } else {
                console.error('Points array is empty for polygon:', coords);
              }
            } else {
              console.error('coords is not a valid array or is empty:', coords);
            }
          });
        } else {
          // Если это просто массив, обрабатываем его как обычно
          if (Array.isArray(polygons) && polygons.length > 0) {
            const points = polygons.map(coord => {
              const longitude = coord[0] * (Math.PI / 180);
              const latitude = coord[1] * (Math.PI / 180);

              // Проверка на NaN
              if (isNaN(longitude) || isNaN(latitude)) {
                console.log("BOTTOM");
                console.error('NaN found in coordinates:', { longitude, latitude });
              }

              const x = radius * Math.cos(latitude) * Math.sin(longitude);
              const y = radius * Math.sin(latitude);
              const z = radius * Math.cos(latitude) * Math.cos(longitude);

              // Проверка на NaN после вычисления
              if (isNaN(x) || isNaN(y) || isNaN(z)) {
                console.error('NaN found in computed coordinates:', { x, y, z });
              }

              return new THREE.Vector3(x, y, z);
            });

            // Проверка на пустой массив points
            if (points.length > 0) {
              // Создаем линию для каждого полигона
              const geometry = new THREE.BufferGeometry().setFromPoints(points);
              const line = new THREE.Line(geometry, lineMaterial);
              scene.add(line);
            } else {
              console.error('Points array is empty for polygon:', polygons);
            }
          } else {
            console.error('polygonCoords is not a valid array or is empty:', polygons);
          }
        }
      });
    },
    addCountriesFromCoordinates(scene, coordinates, radius, thickness = 0.1) {
      const countriesGroup = new THREE.Group(); // Создаем группу для стран
      scene.add(countriesGroup); // Добавляем группу в сцену

      // Проходим по каждому имени в coordinates
      Object.entries(coordinates).forEach(([name, polygons]) => {
        // Проверяем, является ли polygons массивом
        if (Array.isArray(polygons)) {
          polygons.forEach((polygonCoords, index) => {
            // Проверяем, является ли polygonCoords массивом массивов
            if (Array.isArray(polygonCoords[0])) {
              const topPoints = [];
              const bottomPoints = [];

              // Создаем точки для верхней и нижней поверхности
              polygonCoords.forEach(coord => {
                const longitude = coord[0] * (Math.PI / 180);
                const latitude = coord[1] * (Math.PI / 180);
                const x = radius * Math.cos(latitude) * Math.sin(longitude);
                const y = radius * Math.sin(latitude);
                const z = radius * Math.cos(latitude) * Math.cos(longitude);

                // Добавляем верхнюю точку
                topPoints.push(new THREE.Vector3(x, y, z));

                // Добавляем нижнюю точку, смещенную от центра сферы
                const bottomX = (radius + thickness) * Math.cos(latitude) * Math.sin(longitude);
                const bottomY = (radius + thickness) * Math.sin(latitude);
                const bottomZ = (radius + thickness) * Math.cos(latitude) * Math.cos(longitude);
                bottomPoints.push(new THREE.Vector3(bottomX, bottomY, bottomZ));
              });

              // Создаем геометрию для верхней и нижней поверхности
              const geometry = new THREE.BufferGeometry();
              const vertices = [];

              // Добавляем верхние и нижние точки
              topPoints.forEach((point, i) => {
                vertices.push(point.x, point.y, point.z); // Верхняя точка
                vertices.push(bottomPoints[i].x, bottomPoints[i].y, bottomPoints[i].z); // Нижняя точка
              });

              // Создаем индексы для треугольников
              const indices = [];
              for (let i = 0; i < topPoints.length - 1; i++) {
                const topIndex = i * 2;
                const bottomIndex = topIndex + 1;

                // Создаем два треугольника для каждой пары точек
                indices.push(topIndex, bottomIndex, topIndex + 2); // Первый треугольник
                indices.push(bottomIndex, bottomIndex + 2, topIndex + 2); // Второй треугольник
              }

              // Добавляем вершины и индексы в геометрию
              geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
              geometry.setIndex(indices);
              geometry.computeVertexNormals(); // Вычисляем нормали для освещения

              const countryMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00, side: THREE.DoubleSide });
              const countryMesh = new THREE.Mesh(geometry, countryMaterial);

              // Добавляем имя к мешу
              countryMesh.name = `${name}_polygon_${index}`;

              countriesGroup.add(countryMesh); // Добавляем меш страны в группу
            } else {
              console.error('polygonCoords is not an array of arrays:', polygonCoords);
            }
          });
          console.log(countriesGroup);
        } else {
          console.error('polygons is not an array:', polygons);
        }
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