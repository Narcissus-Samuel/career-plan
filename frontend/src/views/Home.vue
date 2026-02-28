<template>
  <div class="home-container">
    <!-- 顶部导航 -->
    <el-header style="background-color: #409EFF; color: #fff; text-align: center; font-size: 22px; line-height: 60px;">
      🎯 大学生职业规划智能体 · 让每一份努力都不被辜负
    </el-header>

    <!-- 主内容区 -->
    <el-main style="background-color: #f5f7fa; padding: 20px;">
      <!-- 欢迎语和统计卡片 -->
      <el-row :gutter="20" style="margin-bottom: 30px;">
        <el-col :span="16">
          <el-card shadow="hover" style="border-radius: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">欢迎回来，同学 👋</div>
            <div style="font-size: 16px;">2025年应届生突破1200万，别让迷茫耽误你的青春。我们用AI为你定制专属职业路径，助你赢在起跑线。</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" style="border-radius: 10px;">
            <el-row :gutter="10">
              <el-col :span="12">
                <div style="text-align: center;">
                  <div style="font-size: 32px; color: #409EFF;">12k+</div>
                  <div style="font-size: 14px; color: #666;">岗位数据</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div style="text-align: center;">
                  <div style="font-size: 32px; color: #67C23A;">8k+</div>
                  <div style="font-size: 14px; color: #666;">学生使用</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </el-col>
      </el-row>

      <!-- 第一步：自我探索（兴趣/专业/行业/职位） -->
      <el-card shadow="hover" style="margin-bottom: 30px; border-radius: 10px;">
        <template #header>
          <span style="font-weight: bold; font-size: 18px;">🔍 第一步：自我探索 · 找到你的方向</span>
          <span style="float: right; font-size: 14px; color: #999;">完成探索后解锁更精准的匹配</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" style="text-align: center; padding: 20px 0; cursor: pointer;" @click="$router.push('/interest')">
              <div style="font-size: 40px; color: #F56C6C;">🎨</div>
              <div style="font-weight: bold; margin: 10px 0;">兴趣探索</div>
              <div style="font-size: 13px; color: #666;">霍兰德AI测评，发现你的职业倾向</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" style="text-align: center; padding: 20px 0; cursor: pointer;" @click="$router.push('/major')">
              <div style="font-size: 40px; color: #409EFF;">📚</div>
              <div style="font-weight: bold; margin: 10px 0;">专业探索</div>
              <div style="font-size: 13px; color: #666;">你的专业能做什么？升学/考公/就业全解析</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" style="text-align: center; padding: 20px 0; cursor: pointer;" @click="$router.push('/industry')">
              <div style="font-size: 40px; color: #67C23A;">🏭</div>
              <div style="font-weight: bold; margin: 10px 0;">行业探索</div>
              <div style="font-size: 13px; color: #666;">了解行业趋势、代表企业、人才需求</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" style="text-align: center; padding: 20px 0; cursor: pointer;" @click="$router.push('/position')">
              <div style="font-size: 40px; color: #E6A23C;">💼</div>
              <div style="font-weight: bold; margin: 10px 0;">职位探索</div>
              <div style="font-size: 13px; color: #666;">岗位职责、发展路径、必备技能全知道</div>
            </el-card>
          </el-col>
        </el-row>
      </el-card>

      <!-- 第二步：能力画像与匹配 -->
      <el-row :gutter="20" style="margin-bottom: 30px;">
        <el-col :span="12">
          <el-card shadow="hover" style="border-radius: 10px; height: 100%;">
            <template #header>
              <span style="font-weight: bold; font-size: 18px;">📄 第二步：上传简历 / 录入信息</span>
            </template>
            <div style="text-align: center; padding: 30px 0;">
              <el-button type="primary" size="large" icon="Upload" @click="$router.push('/student-info')" style="width: 200px; margin-bottom: 15px;">上传简历</el-button>
              <div style="font-size: 14px; color: #666;">支持PDF/Word，AI自动解析能力画像</div>
              <div style="margin-top: 15px;">
                <el-tag type="success" size="small">已解析 2.3w+ 份简历</el-tag>
                <el-tag type="info" size="small" style="margin-left: 10px;">准确率 92%</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover" style="border-radius: 10px; height: 100%;">
            <template #header>
              <span style="font-weight: bold; font-size: 18px;">⚡ 第三步：人岗匹配与报告</span>
            </template>
            <el-row :gutter="10" style="text-align: center; padding: 20px 0;">
              <el-col :span="12">
                <el-button type="warning" icon="DataAnalysis" @click="$router.push('/match-result')" style="width: 90%;">查看匹配结果</el-button>
              </el-col>
              <el-col :span="12">
                <el-button type="success" icon="Document" @click="$router.push('/report')" style="width: 90%;">生成规划报告</el-button>
              </el-col>
            </el-row>
            <div style="margin-top: 10px;">
              <el-progress :percentage="78" status="success" :show-text="false" style="width: 100%;"></el-progress>
              <div style="font-size: 13px; color: #666; margin-top: 5px;">你的竞争力已超过78%的同专业同学</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 第四步：岗位图谱与创新功能 -->
      <el-row :gutter="20" style="margin-bottom: 30px;">
        <el-col :span="16">
          <el-card shadow="hover" style="border-radius: 10px;">
            <template #header>
              <span style="font-weight: bold; font-size: 18px;">🗺️ 岗位图谱 · 发展路径可视化</span>
              <el-button type="text" style="float: right;" @click="$router.push('/job-portrait')">查看更多</el-button>
            </template>
            <el-row :gutter="10">
              <el-col :span="8" v-for="job in hotJobs" :key="job.name">
                <el-card shadow="hover" style="text-align: center; margin-bottom: 10px; cursor: pointer;" @click="$router.push(`/job-portrait?name=${job.name}`)">
                  <div style="font-weight: bold;">{{ job.name }}</div>
                  <div style="font-size: 12px; color: #666;">{{ job.path }}</div>
                </el-card>
              </el-col>
            </el-row>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" style="border-radius: 10px;">
            <template #header>
              <span style="font-weight: bold; font-size: 18px;">✨ 创新工具</span>
            </template>
            <div style="padding: 10px 0;">
              <el-button type="text" icon="ChatDotRound" @click="$router.push('/chat')" style="margin-bottom: 10px;">智能问答助手</el-button><br>
              <el-button type="text" icon="Edit" @click="$router.push('/resume-optimize')" style="margin-bottom: 10px;">简历优化建议</el-button><br>
              <el-button type="text" icon="DataLine" @click="$router.push('/job-compare')" style="margin-bottom: 10px;">岗位对比分析</el-button><br>
              <el-button type="text" icon="UserFilled" @click="$router.push('/role-model')" style="margin-bottom: 10px;">职业榜样故事</el-button><br>
              <el-button type="text" icon="Share" @click="generatePoster" style="margin-bottom: 10px;">生成分享海报</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 行业趋势与热门推荐 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" style="border-radius: 10px;">
            <template #header>
              <span style="font-weight: bold; font-size: 18px;">📈 行业趋势 · 实时洞察</span>
            </template>
            <div v-for="trend in industryTrends" :key="trend.title" style="margin-bottom: 10px;">
              <div style="font-weight: bold;">{{ trend.title }}</div>
              <div style="font-size: 13px; color: #666;">{{ trend.desc }}</div>
              <el-divider style="margin: 8px 0;"></el-divider>
            </div>
            <div style="text-align: right;">
              <el-button type="text" @click="$router.push('/industry')">更多行业报告 →</el-button>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover" style="border-radius: 10px;">
            <template #header>
              <span style="font-weight: bold; font-size: 18px;">📚 推荐学习资源</span>
            </template>
            <el-timeline>
              <el-timeline-item v-for="res in learningResources" :key="res.title" :timestamp="res.type" placement="top">
                <a :href="res.link" target="_blank" style="text-decoration: none; color: #409EFF;">{{ res.title }}</a>
                <div style="font-size: 12px; color: #666;">{{ res.source }}</div>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>
    </el-main>

    <!-- 页脚 -->
    <el-footer style="text-align: center; color: #666; padding: 20px 0; border-top: 1px solid #e6e6e6;">
      大学生职业规划智能体 ©2026 版权所有 | 让职业规划更轻松 · 惠及每一个人
    </el-footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 热门岗位数据（模拟）
const hotJobs = ref([
  { name: '数据分析师', path: '初级 → 中级 → 高级 → 主管' },
  { name: '前端开发', path: '初级 → 中级 → 高级 → 架构师' },
  { name: '产品经理', path: '助理 → 经理 → 总监 → CEO' },
  { name: 'UI设计师', path: '初级 → 资深 → 设计总监' },
  { name: 'Java开发', path: '初级 → 中级 → 高级 → 专家' },
  { name: '运维工程师', path: '初级 → 中级 → 高级 → 架构师' }
])

// 行业趋势数据（模拟）
const industryTrends = ref([
  { title: 'AI大模型人才需求暴涨', desc: '2025年Q1 AI相关岗位同比增长30%，平均薪资超35K' },
  { title: '新能源行业持续火热', desc: '电池/电控/自动驾驶领域人才缺口达50万' },
  { title: '跨境电商运营需求旺盛', desc: 'TikTok/Shopee运营岗位增加45%，小语种加分' }
])

// 推荐学习资源（模拟）
const learningResources = ref([
  { title: '【数据分析】SQL入门到实战', type: 'B站课程', source: '尚硅谷', link: 'https://www.bilibili.com' },
  { title: '【前端】Vue3最新教程', type: '免费公开课', source: '慕课网', link: 'https://www.imooc.com' },
  { title: '【产品经理】从0到1做产品', type: '书籍推荐', source: '人人都是产品经理', link: '#' }
])

// 生成海报功能（模拟）
const generatePoster = () => {
  ElMessage.success('海报生成中，请稍候...（实际调用html2canvas）')
  // 实际实现可使用 html2canvas 捕获指定区域
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.el-header, .el-footer {
  flex-shrink: 0;
}
.el-main {
  flex: 1;
}
.el-card {
  transition: transform 0.3s;
}
.el-card:hover {
  transform: translateY(-3px);
}
</style>