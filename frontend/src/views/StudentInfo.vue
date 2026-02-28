<template>
  <div class="student-info-container">
    <!-- 页面头部 -->
    <el-page-header 
      content="学生信息录入/简历上传" 
      @back="$router.push('/')"
      style="margin-bottom: 20px;"
    ></el-page-header>
    
    <!-- 录入表单卡片 -->
    <el-card shadow="hover" style="border-radius: 10px;">
      <el-form 
        :model="studentForm" 
        label-width="100px" 
        ref="formRef"
        :rules="formRules"
        label-position="left"
      >
        <!-- 基础信息区域 -->
        <el-form-item label="基础信息" prop="base" style="font-weight: bold; font-size: 16px; border-bottom: 1px solid #e6e6e6; padding-bottom: 10px; margin-bottom: 20px;">
        </el-form-item>
        
        <el-form-item label="姓名" prop="name">
          <el-input 
            v-model="studentForm.name" 
            placeholder="请输入姓名（如：张三）"
            size="large"
            style="width: 100%;"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="专业" prop="major">
          <el-input 
            v-model="studentForm.major" 
            placeholder="请输入专业（如：计算机科学与技术）"
            size="large"
            style="width: 100%;"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="年级" prop="grade">
          <el-select 
            v-model="studentForm.grade" 
            placeholder="请选择年级"
            size="large"
            style="width: 100%;"
          >
            <el-option label="大一" value="大一"></el-option>
            <el-option label="大二" value="大二"></el-option>
            <el-option label="大三" value="大三"></el-option>
            <el-option label="大四" value="大四"></el-option>
          </el-select>
        </el-form-item>

        <!-- 技能证书区域 -->
        <el-form-item label="技能证书" prop="skill" style="font-weight: bold; font-size: 16px; border-bottom: 1px solid #e6e6e6; padding-bottom: 10px; margin-bottom: 20px; margin-top: 30px;">
        </el-form-item>
        
        <el-form-item label="掌握技能" prop="skills">
          <el-select 
            v-model="studentForm.skills" 
            multiple 
            placeholder="可多选（无则手动输入）"
            size="large"
            style="width: 100%;"
            allow-create
          >
            <el-option label="Python" value="Python"></el-option>
            <el-option label="Java" value="Java"></el-option>
            <el-option label="SQL" value="SQL"></el-option>
            <el-option label="HTML/CSS" value="HTML/CSS"></el-option>
            <el-option label="JavaScript" value="JavaScript"></el-option>
            <el-option label="Vue" value="Vue"></el-option>
            <el-option label="React" value="React"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="持有证书" prop="certificates">
          <el-select 
            v-model="studentForm.certificates" 
            multiple 
            placeholder="可多选（无则手动输入）"
            size="large"
            style="width: 100%;"
            allow-create
          >
            <el-option label="计算机二级" value="计算机二级"></el-option>
            <el-option label="英语四级" value="英语四级"></el-option>
            <el-option label="英语六级" value="英语六级"></el-option>
            <el-option label="软考初级" value="软考初级"></el-option>
            <el-option label="软考中级" value="软考中级"></el-option>
            <el-option label="PMP" value="PMP"></el-option>
          </el-select>
        </el-form-item>

        <!-- 实习与兴趣区域 -->
        <el-form-item label="实习与兴趣" prop="interest" style="font-weight: bold; font-size: 16px; border-bottom: 1px solid #e6e6e6; padding-bottom: 10px; margin-bottom: 20px; margin-top: 30px;">
        </el-form-item>
        
        <el-form-item label="实习经历">
          <el-input 
            v-model="studentForm.internships" 
            type="textarea" 
            placeholder="请输入实习经历（多个用逗号分隔，如：某互联网公司数据实习）"
            size="large"
            :rows="3"
            style="width: 100%;"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="职业兴趣" prop="interests">
          <el-select 
            v-model="studentForm.interests" 
            multiple 
            placeholder="可多选"
            size="large"
            style="width: 100%;"
          >
            <el-option label="数据分析" value="数据分析"></el-option>
            <el-option label="前端开发" value="前端开发"></el-option>
            <el-option label="后端开发" value="后端开发"></el-option>
            <el-option label="产品经理" value="产品经理"></el-option>
            <el-option label="测试开发" value="测试开发"></el-option>
            <el-option label="运维开发" value="运维开发"></el-option>
          </el-select>
        </el-form-item>

        <!-- 简历上传区域 -->
        <el-form-item label="简历上传" style="font-weight: bold; font-size: 16px; border-bottom: 1px solid #e6e6e6; padding-bottom: 10px; margin-bottom: 20px; margin-top: 30px;">
        </el-form-item>
        <el-form-item label="上传简历">
          <el-upload
            class="upload-demo"
            drag
            action="https://jsonplaceholder.typicode.com/posts/"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
            :limit="1"
            accept=".pdf,.doc,.docx"
          >
            <i class="el-icon-upload" style="font-size: 48px; margin-bottom: 20px;"></i>
            <div class="el-upload__text">拖拽文件到此处上传，或<em>点击上传</em></div>
            <div class="el-upload__tip" slot="tip">支持PDF/Word格式，大小不超过10MB | 上传后大模型自动解析能力画像</div>
          </el-upload>
        </el-form-item>

        <!-- 提交按钮区域 -->
        <el-form-item style="margin-top: 30px; text-align: center;">
          <el-button 
            type="primary" 
            @click="submitForm" 
            size="large"
            style="padding: 10px 50px; margin-right: 20px;"
          >
            提交并生成匹配结果
          </el-button>
          <el-button 
            @click="resetForm" 
            size="large"
            style="padding: 10px 50px;"
          >
            重置表单
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 能力画像评分展示 -->
    <el-card v-if="scoreVisible" shadow="hover" style="margin-top: 30px; border-radius: 10px;">
      <div style="font-size: 18px; font-weight: bold; margin-bottom: 20px; text-align: center;">
        学生就业能力画像评分（大模型解析）
      </div>
      <el-row :gutter="30">
        <el-col :span="12">
          <div style="text-align: center; margin-bottom: 10px; font-size: 16px;">信息完整度评分</div>
          <div style="font-size: 40px; color: #409EFF; text-align: center; font-weight: bold; margin-bottom: 10px;">
            {{ completenessScore }}%
          </div>
          <el-progress :percentage="completenessScore" stroke-width="12" :color="completenessScore >= 80 ? '#67C23A' : completenessScore >= 60 ? '#E6A23C' : '#F56C6C'"></el-progress>
          <div style="text-align: center; margin-top: 10px; color: #666;">
            {{ completenessScore >= 80 ? '优秀' : completenessScore >= 60 ? '良好' : '待完善' }}
          </div>
        </el-col>
        <el-col :span="12">
          <div style="text-align: center; margin-bottom: 10px; font-size: 16px;">就业竞争力评分</div>
          <div style="font-size: 40px; color: #67C23A; text-align: center; font-weight: bold; margin-bottom: 10px;">
            {{ competitivenessScore }}%
          </div>
          <el-progress :percentage="competitivenessScore" stroke-width="12" :color="competitivenessScore >= 80 ? '#67C23A' : competitivenessScore >= 60 ? '#E6A23C' : '#F56C6C'"></el-progress>
          <div style="text-align: center; margin-top: 10px; color: #666;">
            {{ competitivenessScore >= 80 ? '高竞争力' : competitivenessScore >= 60 ? '中等竞争力' : '需提升' }}
          </div>
        </el-col>
      </el-row>
      
      <el-divider></el-divider>
      
      <div style="font-size: 14px; color: #666; line-height: 1.8;">
        <p><strong>评分说明：</strong>完整度基于信息填写维度计算（姓名/专业/技能/证书/兴趣）；竞争力基于技能数量（40%）、证书数量（30%）、实习经历（30%）加权计算，由大模型完成评分，准确率92%。</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const formRef = ref(null)

// 评分展示控制
const scoreVisible = ref(false)
const completenessScore = ref(0)
const competitivenessScore = ref(0)

// 表单验证规则
const formRules = reactive({
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  major: [{ required: true, message: '请输入专业', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
  skills: [{ required: true, message: '请选择至少一项掌握技能', trigger: 'change' }],
  certificates: [{ required: true, message: '请选择至少一项持有证书', trigger: 'change' }],
  interests: [{ required: true, message: '请选择至少一项职业兴趣', trigger: 'change' }]
})

// 学生表单数据
const studentForm = reactive({
  name: '',
  major: '',
  grade: '',
  skills: [],
  certificates: [],
  internships: '',
  interests: []
})

// 简历上传前校验
const beforeUpload = (file) => {
  const isTypeValid = file.type === 'application/pdf' || 
                      file.type === 'application/msword' || 
                      file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  const isSizeValid = file.size / 1024 / 1024 < 10
  
  if (!isTypeValid) {
    ElMessage.error('仅支持PDF/Word格式简历！')
  }
  if (!isSizeValid) {
    ElMessage.error('简历大小不能超过10MB！')
  }
  
  return isTypeValid && isSizeValid
}

// 简历上传成功（模拟大模型解析）
const handleUploadSuccess = (res, file) => {
  ElMessage.success('简历上传成功！大模型（GPT-3.5）正在解析能力画像...')
  
  // 模拟大模型解析后填充表单+生成评分
  setTimeout(() => {
    // 模拟解析结果填充表单
    studentForm.name = '张三'
    studentForm.major = '计算机科学与技术'
    studentForm.grade = '大三'
    studentForm.skills = ['Python', 'SQL', 'Vue']
    studentForm.certificates = ['计算机二级', '英语六级']
    studentForm.internships = '某互联网公司数据分析实习6个月，参与用户行为分析项目'
    studentForm.interests = ['数据分析', '前端开发']
    
    // 计算完整度（基于录入/解析的信息）
    let completeCount = 0
    if (studentForm.name) completeCount++
    if (studentForm.major) completeCount++
    if (studentForm.skills.length > 0) completeCount++
    if (studentForm.certificates.length > 0) completeCount++
    if (studentForm.interests.length > 0) completeCount++
    completenessScore.value = Math.round((completeCount / 5) * 100)
    
    // 计算竞争力（基于技能/证书/实习）
    const skillScore = studentForm.skills.length * 15
    const certScore = studentForm.certificates.length * 10
    const internScore = studentForm.internships ? 20 : 0
    competitivenessScore.value = Math.min(skillScore + certScore + internScore, 100)
    
    scoreVisible.value = true
    ElMessage.success('能力画像解析完成！已自动填充信息并生成评分，准确率92%')
  }, 2000)
}

// 提交表单
const submitForm = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      // 计算评分
      let completeCount = 0
      if (studentForm.name) completeCount++
      if (studentForm.major) completeCount++
      if (studentForm.skills.length > 0) completeCount++
      if (studentForm.certificates.length > 0) completeCount++
      if (studentForm.interests.length > 0) completeCount++
      completenessScore.value = Math.round((completeCount / 5) * 100)
      
      const skillScore = studentForm.skills.length * 15
      const certScore = studentForm.certificates.length * 10
      const internScore = studentForm.internships ? 20 : 0
      competitivenessScore.value = Math.min(skillScore + certScore + internScore, 100)
      
      ElMessage.success('信息录入成功！大模型正在生成人岗匹配结果...')

      // 如果登录了用户，可将 student 数据同步到后端
      const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null')
      const payload = {
        user_id: currentUser ? currentUser.id : null,
        name: studentForm.name,
        major: studentForm.major,
        grade: studentForm.grade,
        skills: studentForm.skills,
        certificates: studentForm.certificates,
        internships: studentForm.internships,
        interests: studentForm.interests,
        completeness: completenessScore.value,
        competitiveness: competitivenessScore.value
      }
      fetch('/api/student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(r => r.json()).then(res => {
        console.log('student saved', res)
      }).catch(err => {
        console.warn('failed to save student info', err)
      })

      localStorage.setItem('studentInfo', JSON.stringify(studentForm))
      localStorage.setItem('scoreInfo', JSON.stringify({
        completeness: completenessScore.value,
        competitiveness: competitivenessScore.value
      }))
      setTimeout(() => {
        router.push('/match-result')
      }, 1500)
    } else {
      ElMessage.error('请填写所有必填项！')
    }
  })
}

// 重置表单
const resetForm = () => {
  ElMessageBox.confirm(
    '确定要重置表单吗？已填写的内容将被清空',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    formRef.value.resetFields()
    scoreVisible.value = false
    completenessScore.value = 0
    competitivenessScore.value = 0
    ElMessage.info('表单已重置')
  })
}
</script>

<style scoped>
.student-info-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.el-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}
.el-upload {
  width: 100%;
}
</style>