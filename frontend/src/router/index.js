import { createRouter, createWebHistory } from 'vue-router';
import ItemList from '../components/ItemList.vue';
import ItemCreate from '../components/ItemCreate.vue';

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
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;