import { createRouter, createWebHistory } from 'vue-router';
import ItemList from '../components/ItemList.vue';
import ItemCreate from '../components/ItemCreate.vue';
import PlanetComponent from '../components/PlanetComponent.vue';
import PlanetComponentV2 from '../components/PlanetComponentV2.vue';
import PlanetComponentV1 from '../components/PlanetComponentV1.vue';
import TownComponent from '../components/TownComponent.vue';

const routes = [
  {
    path: '/',
    name: 'ItemList',
    component: ItemList
  },
  {
    path: '/create',
    name: 'ItemCreate',
    component: ItemCreate
  },
  {
    path: '/planet',
    name: 'Planet',
    component: PlanetComponent
  },
  {
    path: '/planetV1',
    name: 'PlanetV1',
    component: PlanetComponentV1
  },
  {
    path: '/planetV2',
    name: 'PlanetV2',
    component: PlanetComponentV2
  },
  {
    path: '/town',
    name: 'Town',
    component: TownComponent
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;