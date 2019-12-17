import Vue from 'vue'
import Router from 'vue-router'
import Config from '@/components/Config'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/config',
      name: 'Config',
      component: Config
    }
  ]
})
