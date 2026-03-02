<template>
  <div class="admin-dashboard container">
    <h2>管理员后台</h2>
    <div class="controls">
      <button @click="fetchUsers">刷新用户列表</button>
    </div>
    <table class="user-table">
      <thead>
        <tr><th>ID</th><th>用户名</th><th>手机号</th><th>角色</th><th>操作</th></tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>{{ u.id }}</td>
          <td>{{ u.username }}</td>
          <td>{{ u.phone }}</td>
          <td>{{ u.role }}</td>
          <td>
            <button @click="setRole(u.id, u.role === 'admin' ? 'user' : 'admin')">切换角色</button>
            <button @click="deleteUser(u.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'AdminDashboard',
  data() { return { users: [] } },
  mounted() { this.fetchUsers() },
  methods: {
    async fetchUsers() {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await axios.get('/api/admin/users', { headers: { Authorization: `Bearer ${token}` } })
        this.users = res.data.users
      } catch (e) { alert('获取用户失败：' + (e.response?.data?.error || e.message)) }
    },
    async setRole(id, role) {
      try {
        const token = localStorage.getItem('admin_token')
        await axios.put(`/api/admin/users/${id}`, { role }, { headers: { Authorization: `Bearer ${token}` } })
        this.fetchUsers()
      } catch (e) { alert('操作失败') }
    },
    async deleteUser(id) {
      if (!confirm('确定删除该用户？')) return
      try {
        const token = localStorage.getItem('admin_token')
        await axios.delete(`/api/admin/users/${id}`, { headers: { Authorization: `Bearer ${token}` } })
        this.fetchUsers()
      } catch (e) { alert('删除失败') }
    }
  }
}
</script>

<style scoped>
.admin-dashboard{max-width:1100px;margin:40px auto;padding:20px;background:#fff;border-radius:8px}
.user-table{width:100%;border-collapse:collapse}
.user-table th,.user-table td{border:1px solid #eee;padding:8px;text-align:left}
</style>
