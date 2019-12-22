import Vue from 'vue'
import Router from 'vue-router'
import Config from '@/components/Config'
import Home from '@/components/Home'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/config',
      name: 'Config',
      component: Config
    }
  ]
})
