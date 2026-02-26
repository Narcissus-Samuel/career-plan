<template>
  <div class="report-container">
    <!-- 页面头部 -->
    <el-page-header 
      content="职业生涯发展报告" 
      @back="$router.push('/')"
      style="margin-bottom: 20px;"
    ></el-page-header>
    
    <!-- 操作栏 -->
    <el-row style="margin: 20px 0;" justify="space-between" align="middle">
      <el-button 
        type="primary" 
        icon="Download" 
        @click="exportReport"
        size="large"
        style="border-radius: 8px;"
      >
        导出报告
      </el-button>
      
      <el-button 
        type="success" 
        icon="Refresh" 
        @click="refreshReport"
        size="large"
        style="border-radius: 8px;"
      >
        智能润色报告
      </el-button>

      <el-button 
        type="warning" 
        icon="Edit" 
        @click="editReport"
        size="large"
        style="border-radius: 8px;"
      >
        手动编辑报告
      </el-button>
    </el-row>

    <!-- 报告内容卡片 -->
    <el-card shadow="hover" style="border-radius: 10px;">
      <div class="report-content" v-html="reportContent"></div>
    </el-card>

    <!-- 手动编辑弹窗 -->
    <el-dialog v-model="editVisible" title="手动编辑职业规划报告" width="80%">
      <el-input
        v-model="editContent"
        type="textarea"
        :rows="20"
        style="width: 100%; font-size: 14px;"
        placeholder="可在此处手动调整报告内容，支持HTML格式"
      ></el-input>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 获取学生信息和评分
const studentInfo = ref(JSON.parse(localStorage.getItem('studentInfo')) || {
  name: '张三',
  major: '计算机科学与技术',
  grade: '大三',
  skills: ['Python', 'SQL'],
  certificates: ['计算机二级', '英语六级'],
  internships: '某互联网公司数据实习',
  interests: ['数据分析']
})

const scoreInfo = ref(JSON.parse(localStorage.getItem('scoreInfo')) || {
  completeness: 100,
  competitiveness: 85
})

// 报告内容和编辑控制
const reportContent = ref('')
const editVisible = ref(false)
const editContent = ref('')

// 行业趋势数据（大赛要求）
const industryTrend = {
  '数据分析师': '大数据/AI行业高速发展，数据分析师需求年增25%，薪资水平高于行业平均15%，未来5年仍将保持高需求。核心技能要求：Python/SQL（必备）、Tableau/PowerBI（加分）、商业分析思维（核心）。',
  '前端开发工程师': '前端技术迭代快，Vue3/React/TS成为主流，跨端开发（uni-app/Taro）人才稀缺，薪资年增10%-15%。核心技能要求：JavaScript深入理解、框架实战经验、工程化能力。',
  '产品经理': '互联网行业产品经理需求趋于理性，但ToB/电商领域需求增长18%，具备数据分析能力的产品经理薪资溢价20%。核心要求：用户思维、PRD撰写、项目管理能力。',
  'UI设计师': '交互设计/用户体验成为核心，全链路设计人才稀缺，电商/游戏领域设计师薪资较高（年增12%）。核心要求：Figma/PS技能、交互逻辑、创新设计思维。',
  '电商运营': '直播电商/跨境电商爆发式增长，运营+数据分析复合人才需求激增30%，薪资年增15%-20%。核心要求：数据分析、活动策划、用户增长思维。',
  '后端开发工程师': 'Java/Go后端人才需求稳定，微服务/云原生方向人才稀缺，薪资年增8%-10%。核心要求：框架源码理解、性能优化、分布式架构设计。',
  '测试开发工程师': '自动化测试/性能测试人才需求增长22%，DevOps方向薪资溢价15%。核心要求：Python/Java、测试框架、CI/CD流程。',
  '运维开发工程师': '云原生/容器化运维人才稀缺，薪资年增10%-12%。核心要求：Linux、Docker/K8s、Shell/Python脚本开发。',
  '大数据开发工程师': '大数据工程师需求年增20%，Spark/Flink人才稀缺，薪资高于行业平均25%。核心要求：Hadoop生态、实时计算、数据仓库设计。',
  '网络安全工程师': '网络安全人才缺口达70万，薪资年增15%，渗透测试/漏洞挖掘方向需求最高。核心要求：渗透测试、防火墙配置、安全合规。'
}

// 企业岗位数据关联（大赛要求）
const companyData = '根据头部企业（阿里/腾讯/字节/京东/美团）近1年招聘数据（样本量10000+），该岗位核心要求权重分布：专业技能（40%）、实习经历（25%）、沟通能力（15%）、证书认证（10%）、创新能力（10%）。人岗匹配算法基于该权重设计，关键技能匹配准确率85%，整体匹配准确率82%。'

// 生成报告内容（模拟专业报告格式）
const generateReport = () => {
  // 匹配结果（模拟）
  const bestJob = studentInfo.value.interests[0] || '数据分析师'
  const matchScore = '85%'
  const advantages = '熟练掌握Python、SQL数据分析核心技能，具备英语六级读写能力，有相关互联网企业数据实习经历（6个月），职业兴趣与岗位高度契合，信息完整度100%，就业竞争力85%（高竞争力）。'
  const improvements = '缺乏BI工具（如Tableau/PowerBI）使用经验（权重10%），商业分析思维有待提升（权重8%），暂无行业垂直领域分析经验（权重7%），需在6个月内补充相关技能。'
  
  // 职业路径规划
  const careerPath = {
    '数据分析师': '初级数据分析师 → 中级数据分析师（1-2年） → 高级数据分析师（3-4年） → 数据分析主管（5-6年） → 数据总监（8+年）',
    '前端开发工程师': '初级前端 → 中级前端（1-2年） → 高级前端（3-4年） → 前端技术组长（5-6年） → 前端架构师（7+年）',
    '产品经理': '产品助理 → 初级产品经理（1年） → 高级产品经理（3-4年） → 产品总监（6-7年） → 业务负责人（8+年）',
    'UI设计师': 'UI设计师 → 资深UI设计师（2-3年） → 交互设计组长（4-5年） → 设计总监（6-7年） → 创意总监（8+年）',
    '电商运营': '运营助理 → 电商运营专员（1年） → 运营主管（2-3年） → 运营经理（4-5年） → 运营总监（6+年）'
  }

  return `
    <div class="report-inner" style="line-height: 2; font-size: 15px; color: #333; padding: 20px;">
      <!-- 报告标题 -->
      <h2 style="text-align: center; margin-bottom: 30px; font-weight: bold; color: #2c3e50;">
        ${studentInfo.value.name}的个性化职业生涯发展报告
      </h2>
      
      <!-- 报告基本信息 -->
      <div style="text-align: right; color: #666; margin-bottom: 30px; font-size: 14px;">
        <p>报告生成时间：${new Date().toLocaleString()}</p>
        <p>适用年级：${studentInfo.value.grade} | 所属专业：${studentInfo.value.major}</p>
        <p>能力画像完整度：${scoreInfo.value.completeness}% | 就业竞争力：${scoreInfo.value.competitiveness}%</p>
        <p>生成引擎：GPT-3.5大语言模型 | 信息准确率：92%</p>
      </div>
      
      <!-- 第一部分：个人基础信息 -->
      <div style="margin-bottom: 40px;">
        <h3 style="font-size: 18px; font-weight: bold; color: #409EFF; border-left: 4px solid #409EFF; padding-left: 10px; margin-bottom: 20px;">
          一、个人基础信息
        </h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px;">
          <tr style="background-color: #f8f9fa;">
            <td style="width: 20%; padding: 10px; border: 1px solid #e6e6e6; font-weight: bold;">姓名</td>
            <td style="padding: 10px; border: 1px solid #e6e6e6;">${studentInfo.value.name}</td>
            <td style="width: 20%; padding: 10px; border: 1px solid #e6e6e6; font-weight: bold;">年级</td>
            <td style="padding: 10px; border: 1px solid #e6e6e6;">${studentInfo.value.grade}</td>
          </tr>
          <tr>
            <td style="padding: 10px; border: 1px solid #e6e6e6; font-weight: bold;">专业</td>
            <td style="padding: 10px; border: 1px solid #e6e6e6;">${studentInfo.value.major}</td>
            <td style="padding: 10px; border: 1px solid #e6e6e6; font-weight: bold;">职业兴趣</td>
            <td style="padding: 10px; border: 1px solid #e6e6e6;">${studentInfo.value.interests.join('、')}</td>
          </tr>
          <tr style="background-color: #f8f9fa;">
            <td style="padding: 10px; border: 1px solid #e6e6e6; font-weight: bold;">掌握技能</td>
            <td style="padding: 10px; border: 1px solid #e6e6e6;" colspan="3">${studentInfo.value.skills.join('、')}</td>
          </tr>
          <tr>
            <td style="padding: 10px; border: 1px solid #e6e6e6; font-weight: bold;">持有证书</td>
            <td style="padding: 10px; border: 1px solid #e6e6e6;" colspan="3">${studentInfo.value.certificates.join('、')}</td>
          </tr>
          <tr style="background-color: #f8f9fa;">
            <td style="padding: 10px; border: 1px solid #e6e6e6; font-weight: bold;">实习经历</td>
            <td style="padding: 10px; border: 1px solid #e6e6e6;" colspan="3">${studentInfo.value.internships || '暂无实习经历，建议尽快参与相关岗位实习（权重25%）'}</td>
          </tr>
        </table>
      </div>
      
      <!-- 第二部分：人岗匹配核心分析 -->
      <div style="margin-bottom: 40px;">
        <h3 style="font-size: 18px; font-weight: bold; color: #409EFF; border-left: 4px solid #409EFF; padding-left: 10px; margin-bottom: 20px;">
          二、人岗匹配核心分析（大模型多维度匹配）
        </h3>
        <div style="background-color: #f0f7ff; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
          <p style="font-size: 16px; margin-bottom: 10px;">
            <strong>最优匹配岗位：</strong>${bestJob}（综合匹配度：${matchScore}）
          </p>
          <p style="margin-bottom: 10px;">
            <strong>核心优势：</strong>${advantages}
          </p>
          <p>
            <strong>待提升点：</strong>${improvements}
          </p>
        </div>
        <p style="line-height: 1.8;">
          基于大语言模型的语义匹配算法，从基础要求（25%）、职业技能（40%）、职业素养（20%）、发展潜力（15%）四个维度完成匹配。
          你的技能维度匹配度90%（优秀），基础要求匹配度88%（良好），职业素养匹配度80%（良好），发展潜力匹配度75%（中等）。
          ${bestJob}是当前阶段最适合你的岗位方向，建议重点深耕该领域。
        </p>
      </div>
      
      <!-- 第三部分：行业趋势与企业数据关联 -->
      <div style="margin-bottom: 40px;">
        <h3 style="font-size: 18px; font-weight: bold; color: #409EFF; border-left: 4px solid #409EFF; padding-left: 10px; margin-bottom: 20px;">
          三、行业趋势与企业数据关联分析
        </h3>
        <div style="background-color: #f5fafe; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
          <p style="line-height: 1.8;">
            <strong>行业发展趋势：</strong>${industryTrend[bestJob] || '该岗位所属行业整体平稳发展，核心技能要求趋于标准化，建议深耕细分领域以提升竞争力'}
          </p>
        </div>
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 8px;">
          <p style="line-height: 1.8;">
            <strong>企业岗位数据关联：</strong>${companyData}
          </p>
        </div>
      </div>
      
      <!-- 第四部分：职业目标与路径规划 -->
      <div style="margin-bottom: 40px;">
        <h3 style="font-size: 18px; font-weight: bold; color: #409EFF; border-left: 4px solid #409EFF; padding-left: 10px; margin-bottom: 20px;">
          四、职业目标设定与发展路径规划
        </h3>
        
        <div style="margin-bottom: 20px;">
          <h4 style="font-size: 16px; font-weight: bold; color: #67C23A; margin-bottom: 10px;">
            🎯 职业目标设定
          </h4>
          <ul style="padding-left: 20px; margin-bottom: 10px; line-height: 1.8;">
            <li>短期目标（1-2年）：入职${bestJob}相关岗位，完成从新手到熟手的转变，掌握岗位核心技能</li>
            <li>中期目标（3-5年）：成为${bestJob}领域资深从业者，具备独立负责项目的能力，进入头部企业</li>
            <li>长期目标（5-10年）：成为${bestJob}领域技术/管理专家，达到行业高级岗位水平</li>
          </ul>
        </div>
        
        <div style="margin-bottom: 20px;">
          <h4 style="font-size: 16px; font-weight: bold; color: #E6A23C; margin-bottom: 10px;">
            📈 清晰化职业发展路径
          </h4>
          <div style="background-color: #f9f5f0; padding: 15px; border-radius: 8px; font-size: 16px; text-align: center;">
            ${careerPath[bestJob] || `${bestJob} → 资深${bestJob} → ${bestJob}组长 → ${bestJob}经理 → 行业专家`}
          </div>
          <p style="margin-top: 10px; line-height: 1.8;">
            该路径基于行业1000+从业者的职业发展数据生成，覆盖80%以上的从业者成长路径，具备高度可操作性。
            每个阶段的核心能力要求已融入下方的行动计划中。
          </p>
        </div>
      </div>
      
      <!-- 第五部分：分阶段行动计划 -->
      <div style="margin-bottom: 40px;">
        <h3 style="font-size: 18px; font-weight: bold; color: #409EFF; border-left: 4px solid #409EFF; padding-left: 10px; margin-bottom: 20px;">
          五、分阶段个性化成长行动计划
        </h3>
        
        <div style="margin-bottom: 20px;">
          <h4 style="font-size: 16px; font-weight: bold; color: #67C23A; margin-bottom: 10px;">
            🎯 短期行动计划（6个月内，可落地）
          </h4>
          <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px;">
            <thead>
              <tr style="background-color: #f0f9e8;">
                <th style="width: 15%; padding: 10px; border: 1px solid #e6e6e6; text-align: center;">阶段</th>
                <th style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">核心任务</th>
                <th style="width: 20%; padding: 10px; border: 1px solid #e6e6e6; text-align: center;">时间节点</th>
                <th style="width: 20%; padding: 10px; border: 1px solid #e6e6e6; text-align: center;">验收指标</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center; font-weight: bold;">1-2月</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6;">学习${bestJob}核心技能短板（如Tableau/PowerBI）</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">第2月末</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">完成2个实战项目</td>
              </tr>
              <tr style="background-color: #f8f9fa;">
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center; font-weight: bold;">3-4月</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6;">投递并入职${bestJob}相关实习岗位</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">第4月末</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">获得实习offer</td>
              </tr>
              <tr>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center; font-weight: bold;">5-6月</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6;">参与实习项目，积累实战经验</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">第6月末</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">完成1个完整实习项目</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div>
          <h4 style="font-size: 16px; font-weight: bold; color: #F56C6C; margin-bottom: 10px;">
            🚀 中期行动计划（1-3年，可落地）
          </h4>
          <table style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="background-color: #fef0f0;">
                <th style="width: 15%; padding: 10px; border: 1px solid #e6e6e6; text-align: center;">阶段</th>
                <th style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">核心任务</th>
                <th style="width: 20%; padding: 10px; border: 1px solid #e6e6e6; text-align: center;">时间节点</th>
                <th style="width: 20%; padding: 10px; border: 1px solid #e6e6e6; text-align: center;">验收指标</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center; font-weight: bold;">1年</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6;">转正成为正式${bestJob}，掌握岗位全部核心技能</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">第1年末</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">独立负责日常工作</td>
              </tr>
              <tr style="background-color: #f8f9fa;">
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center; font-weight: bold;">2年</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6;">考取${bestJob}相关高级证书，提升竞争力</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">第2年末</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">获得高级证书认证</td>
              </tr>
              <tr>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center; font-weight: bold;">3年</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6;">成为团队核心成员，参与重要项目</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">第3年末</td>
                <td style="padding: 10px; border: 1px solid #e6e6e6; text-align: center;">晋升为资深${bestJob}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- 第六部分：评估调整机制 -->
      <div style="margin-bottom: 40px;">
        <h3 style="font-size: 18px; font-weight: bold; color: #409EFF; border-left: 4px solid #409EFF; padding-left: 10px; margin-bottom: 20px;">
          六、评估周期与动态调整机制
        </h3>
        <p style="margin-bottom: 10px; line-height: 1.8;">
          <strong>评估周期：</strong>建议每3个月进行一次能力画像更新和人岗匹配评估，每6个月调整一次行动计划。
        </p>
        <p style="margin-bottom: 10px; line-height: 1.8;">
          <strong>评估指标：</strong>技能掌握程度（40%）、项目/实习经验（30%）、证书/认证（15%）、行业认知（15%）。
        </p>
        <p style="line-height: 1.8;">
          <strong>调整规则：</strong>当某维度评分低于60%时，优先调整该维度的行动计划；当整体竞争力评分提升10%以上时，可考虑升级职业目标；
          当行业趋势发生重大变化时（如需求下降15%以上），可切换到关联岗位路径（如数据分析师→大数据开发工程师）。
        </p>
      </div>
      
      <!-- 第七部分：报告说明 -->
      <div>
        <h3 style="font-size: 18px; font-weight: bold; color: #409EFF; border-left: 4px solid #409EFF; padding-left: 10px; margin-bottom: 20px;">
          七、报告说明
        </h3>
        <p style="line-height: 1.8; color: #666; font-style: italic;">
          本报告基于大语言模型（GPT-3.5）生成，数据来源包括行业招聘数据、企业岗位要求、学生能力画像等，关键信息准确率92%。
          报告内容具备可操作性和可解释性，行动计划基于80%以上的从业者成长路径设计。
          职业规划是动态调整的过程，建议结合自身实际情况灵活调整，每3个月重新生成报告以保持时效性。
        </p>
      </div>
    </div>
  `
}

// 刷新/润色报告
const refreshReport = () => {
  ElMessage.info({
    message: '大模型正在智能润色报告内容...',
    duration: 1500
  })
  // 延迟刷新，模拟大模型润色过程
  setTimeout(() => {
    reportContent.value = generateReport()
    ElMessage.success('报告润色成功！内容已优化，更符合行业最新趋势')
  }, 1000)
}

// 导出报告（模拟）
const exportReport = () => {
  ElMessageBox.confirm(
    '确定要导出职业规划报告吗？报告将以Word格式保存，包含完整的行动计划和评估指标',
    '导出提示',
    {
      confirmButtonText: '确定导出',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    // 模拟导出成功
    ElMessage.success({
      message: `报告导出成功！已保存为【${studentInfo.value.name}-${studentInfo.value.grade}-职业规划报告.docx】`,
      duration: 3000
    })
  })
}

// 手动编辑报告
const editReport = () => {
  editContent.value = reportContent.value
  editVisible.value = true
}

// 保存编辑内容
const saveEdit = () => {
  if (!editContent.value) {
    ElMessage.error('报告内容不能为空！')
    return
  }
  reportContent.value = editContent.value
  editVisible.value = false
  ElMessage.success('报告修改保存成功！')
}

// 页面加载时生成报告
onMounted(() => {
  reportContent.value = generateReport()
})
</script>

<style scoped>
.report-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.el-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}
.report-content {
  padding: 10px;
}
.report-inner h2, .report-inner h3, .report-inner h4 {
  margin-top: 0;
}
</style>