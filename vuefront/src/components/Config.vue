<template>
  <div class="hello">
    <h1>微博舆情监控参数设置</h1>
    <UL>
      <li>最低粉丝数: <input v-model="config.min_fans"></li>
      <li>爬取用户数: <input v-model="config.min_ids"></li>
    </UL>
    <h3>{{message}}</h3>
    <button @click="setConfig">保存参数设置</button>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'Config',
  data () {
    return {
      config: {},
      message: ''
    }
  },
  methods: {
    getConfig () {
      const path = `http://localhost:81/config`
      axios.get(path)
        .then(response => {
          // alert(response.data.config)
          this.config = response.data.config
        })
        .catch(error => {
          console.log(error)
        })
    },
    setConfig () {
      const path = `http://localhost:81/config`
      axios.post(path, this.config)
        .then(response => {
          // alert(response.data.config)
          this.message = response.data.message
        })
        .catch(error => {
          console.log(error)
        })
    }
  },
  created () {
    this.getConfig()
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
