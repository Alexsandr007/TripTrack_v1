import { createRouter, createWebHistory } from 'vue-router';
import ItemList from '../components/ItemList.vue';
import ItemCreate from '../components/ItemCreate.vue';
import PlanetComponent from '../components/PlanetComponent.vue';

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
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;