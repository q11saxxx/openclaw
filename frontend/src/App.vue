<template>
  <el-container style="height:100vh">
    <el-header height="60px">OpenClaw</el-header>
    <el-container>
      <el-aside width="200px">
        <el-menu :default-active="$route.path" router>
          <el-menu-item index="/">Dashboard</el-menu-item>
          <el-menu-item index="/skills">Skills</el-menu-item>
          <el-menu-item index="/audit">Audit</el-menu-item>
          <el-menu-item index="/reports">Reports</el-menu-item>
          <el-menu-item index="/rules">Rules</el-menu-item>
        </el-menu>
      </el-aside>
      <el-main style="padding:16px">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script lang="ts" setup>
</script>
