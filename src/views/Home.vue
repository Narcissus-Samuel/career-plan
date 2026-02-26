<template>
  <div class="home-container">
    <!-- 顶部导航 -->
    <el-header style="background-color: #409EFF; color: #fff; text-align: center; font-size: 22px; line-height: 60px;">
      大学生职业规划智能体
    </el-header>
    
    <!-- 核心功能入口 -->
    <el-main style="flex: 1; padding: 50px 0;">
      <el-row justify="center">
        <el-col :span="12">
          <el-card shadow="hover" style="border-radius: 10px;">
            <div style="font-size: 18px; font-weight: bold; text-align: center; margin-bottom: 30px;">
              核心功能
            </div>
            
            <el-row :gutter="20" style="margin-bottom: 20px;">
              <el-col :span="12">
                <el-button 
                  type="primary" 
                  size="large" 
                  icon="User" 
                  @click="$router.push('/student-info')"
                  style="width: 100%; padding: 25px 0; border-radius: 8px;"
                >
                  学生信息录入/简历上传
                </el-button>
              </el-col>
              <el-col :span="12">
                <el-button 
                  type="success" 
                  size="large" 
                  icon="Document" 
                  @click="$router.push('/report')"
                  style="width: 100%; padding: 25px 0; border-radius: 8px;"
                >
                  查看规划报告
                </el-button>
              </el-col>
            </el-row>
            
            <el-row :gutter="20" style="margin-bottom: 20px;">
              <el-col :span="12">
                <el-button 
                  type="warning" 
                  size="large" 
                  icon="DataAnalysis" 
                  @click="$router.push('/match-result')"
                  style="width: 100%; padding: 25px 0; border-radius: 8px;"
                >
                  查看人岗匹配结果
                </el-button>
              </el-col>
              <el-col :span="12">
                <el-button 
                  type="info" 
                  size="large" 
                  icon="OfficeBuilding" 
                  @click="$router.push('/job-portrait')"
                  style="width: 100%; padding: 25px 0; border-radius: 8px;"
                >
                  岗位画像与发展路径
                </el-button>
              </el-col>
            </el-row>
            
            <el-divider content-position="center">职业规划核心工具</el-divider>
            
            <el-button 
              type="danger" 
              size="large" 
              icon="TrendCharts" 
              @click="$router.push('/job-portrait')"
              style="width: 80%; padding: 20px 0; border-radius: 8px; margin: 0 auto; display: block;"
            >
              查看岗位关联图谱
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
    
    <!-- 页脚 -->
    <el-footer style="text-align: center; color: #666; padding: 20px 0; border-top: 1px solid #e6e6e6;">
      大学生职业规划智能体 ©2026 版权所有 | 基于大语言模型构建
    </el-footer>
  </div>
</template>

<script setup>
// 首页无额外逻辑
</script>

<style scoped>
.home-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.el-header, .el-footer {
  flex-shrink: 0;
}
.el-main {
  flex: 1;
  background-color: #f5f7fa;
}
</style>