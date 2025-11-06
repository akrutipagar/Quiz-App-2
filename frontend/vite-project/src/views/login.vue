<template>
  <div>
    <h2>Login</h2>
    <input v-model="username" placeholder="Username" />
    <input v-model="password" type="password" placeholder="Password" />
    <button @click="login">Login</button>
   
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    async login() {
      try {
  const res = await axios.post('http://localhost:5000/login', {
    username: this.username,
    password: this.password
  }, { withCredentials: true });

  const role = res.data.role;
 

 
    if (role === 'admin') {
      this.$router.push('/admindashboard');
    } else {
      this.$router.push('/userdashboard');
    }
  

} catch (err) {
  alert(err.response?.data?.msg || 'Login failed');
}

     
    }
  }
}



</script>
