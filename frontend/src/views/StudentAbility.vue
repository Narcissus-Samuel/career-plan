<template>
  <div class="student-ability-container">
    <el-page-header content="个人能力信息录入" @back="$router.push('/')"></el-page-header>

    <!-- 分步表单
    <el-steps :active="activeStep" finish-status="success" style="margin: 20px 0;">
      <el-step title="基础信息"></el-step>
      <el-step title="技能证书"></el-step>
      <el-step title="能力自评"></el-step>
      <el-step title="画像生成"></el-step>
    </el-steps> -->

    <!-- <el-card style="margin: 20px 0;"> -->
      <!-- 第一步：基础信息 -->
      <div v-if="activeStep === 0">
        <el-form :model="basicForm" label-width="100px" :rules="basicRules" ref="basicFormRef">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="basicForm.name" placeholder="请输入姓名"></el-input>
          </el-form-item>
          <el-form-item label="性别" prop="gender">
            <el-select v-model="basicForm.gender" placeholder="请选择性别">
              <el-option label="男" value="男"></el-option>
              <el-option label="女" value="女"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="专业" prop="major">
            <el-input v-model="basicForm.major" placeholder="请输入专业"></el-input>
          </el-form-item>
          <el-form-item label="年级" prop="grade">
            <el-select v-model="basicForm.grade" placeholder="请选择年级">
              <el-option label="大一" value="大一"></el-option>
              <el-option label="大二" value="大二"></el-option>
              <el-option label="大三" value="大三"></el-option>
              <el-option label="大四" value="大四"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="学历" prop="education">
            <el-select v-model="basicForm.education" placeholder="请选择学历">
              <el-option label="本科" value="本科"></el-option>
              <el-option label="硕士" value="硕士"></el-option>
              <el-option label="博士" value="博士"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="nextStep">下一步</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 第二步：技能证书 -->
      <div v-if="activeStep === 1">
        <!-- <el-form :model="skillForm" label-width="100px" ref="skillFormRef"> -->
          <!-- 修复：替换 TagInput 为 el-input + el-tag 组合 -->
          <el-form-item label="专业技能">
            <div class="tag-input-container">
              <el-tag
                v-for="(skill, index) in skillForm.skills"
                :key="index"
                closable
                @close="handleTagClose(skillForm.skills, index)"
                style="margin: 0 8px 8px 0;"
              >
                {{ skill }}
              </el-tag>
              <el-input
                v-model="tempSkill"
                placeholder="输入技能后按回车添加（如Python、Java）"
                @keyup.enter="handleTagAdd(skillForm.skills, tempSkill)"
                style="width: 200px; margin-top: 8px;"
              ></el-input>
            </div>
          </el-form-item>
          <el-form-item label="已获证书">
            <div class="tag-input-container">
              <el-tag
                v-for="(cert, index) in skillForm.certificates"
                :key="index"
                closable
                @close="handleTagClose(skillForm.certificates, index)"
                style="margin: 0 8px 8px 0;"
              >
                {{ cert }}
              </el-tag>
              <el-input
                v-model="tempCert"
                placeholder="输入证书后按回车添加（如计算机二级、英语六级）"
                @keyup.enter="handleTagAdd(skillForm.certificates, tempCert)"
                style="width: 200px; margin-top: 8px;"
              ></el-input>
            </div>
          </el-form-item>
          <el-form-item label="实习经历">
            <el-input v-model="skillForm.internship" type="textarea" rows="4" placeholder="请简要描述实习经历"></el-input>
          </el-form-item>
          <el-form-item label="项目经历">
            <el-input v-model="skillForm.project" type="textarea" rows="4" placeholder="请简要描述项目经历"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" @click="nextStep">下一步</el-button>
          </el-form-item>
        <!-- </el-form> -->
      </div>

      <!-- 第三步：能力自评 -->
      <div v-if="activeStep === 2">
        <!-- <el-form :model="abilityForm" label-width="100px" ref="abilityFormRef"> -->
          <el-form-item label="创新能力（0-100）">
            <el-slider v-model="abilityForm.innovation" :max="100" show-input></el-slider>
          </el-form-item>
          <el-form-item label="学习能力（0-100）">
            <el-slider v-model="abilityForm.learning" :max="100" show-input></el-slider>
          </el-form-item>
          <el-form-item label="抗压能力（0-100）">
            <el-slider v-model="abilityForm.pressure" :max="100" show-input></el-slider>
          </el-form-item>
          <el-form-item label="沟通能力（0-100）">
            <el-slider v-model="abilityForm.communication" :max="100" show-input></el-slider>
          </el-form-item>
          <el-form-item label="实习能力（0-100）">
            <el-slider v-model="abilityForm.internship" :max="100" show-input></el-slider>
          </el-form-item>
          <el-form-item>
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" @click="generateAbility">生成能力画像</el-button>
          </el-form-item>
        <!-- </el-form> -->
      </div>

      <!-- 第四步：画像生成 -->
      <div v-if="activeStep === 3">
        <div class="ability-result">
          <!-- <h3>你的能力画像已生成！</h3> -->
          <el-card style="margin: 20px 0;">
            <h4>基础信息</h4>
            <p>姓名：{{ basicForm.name }} | 专业：{{ basicForm.major }} | 年级：{{ basicForm.grade }}</p>
            
            <h4 style="margin-top: 15px;">专业技能</h4>
            <el-tag v-for="skill in skillForm.skills" :key="skill" size="small">{{ skill }}</el-tag>
            
            <h4 style="margin-top: 15px;">能力评分</h4>
            <el-table :data="abilityTableData" border size="small">
              <el-table-column prop="name" label="能力维度"></el-table-column>
              <el-table-column prop="score" label="自评分数"></el-table-column>
              <el-table-column prop="level" label="能力等级">
                <template #default="scope">
                  <el-tag :type="scope.row.score >= 80 ? 'success' : (scope.row.score >= 60 ? 'warning' : 'danger')">
                    {{ scope.row.score >= 80 ? '优秀' : (scope.row.score >= 60 ? '良好' : '待提升') }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
            
            <div style="margin-top: 20px; text-align: center;">
              <el-button type="primary" @click="saveAbility">保存画像并前往匹配</el-button>
              <el-button @click="resetForm" style="margin-left: 10px;">重新录入</el-button>
            </div>
          </el-card>
        </div>
      </div>
    <!-- </el-card> -->
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()

// 分步表单控制
const activeStep = ref(0)

// 临时变量：用于标签输入
const tempSkill = ref('')
const tempCert = ref('')

// 第一步：基础信息表单
const basicFormRef = ref(null)
const basicForm = reactive({
  name: '',
  gender: '',
  major: '',
  grade: '',
  education: ''
})
const basicRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  major: [{ required: true, message: '请输入专业', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
  education: [{ required: true, message: '请选择学历', trigger: 'change' }]
}

// 第二步：技能证书表单
const skillFormRef = ref(null)
const skillForm = reactive({
  skills: [],
  certificates: [],
  internship: '',
  project: ''
})

// 第三步：能力自评表单
const abilityFormRef = ref(null)
const abilityForm = reactive({
  innovation: 80,
  learning: 85,
  pressure: 75,
  communication: 80,
  internship: 70
})

// 能力画像结果表格
const abilityTableData = ref([
  { name: '创新能力', score: abilityForm.innovation, level: '' },
  { name: '学习能力', score: abilityForm.learning, level: '' },
  { name: '抗压能力', score: abilityForm.pressure, level: '' },
  { name: '沟通能力', score: abilityForm.communication, level: '' },
  { name: '实习能力', score: abilityForm.internship, level: '' }
])

// 修复：标签添加方法
const handleTagAdd = (list, value) => {
  if (value.trim() && !list.includes(value.trim())) {
    list.push(value.trim())
    // 清空输入框
    if (list === skillForm.skills) {
      tempSkill.value = ''
    } else if (list === skillForm.certificates) {
      tempCert.value = ''
    }
  } else if (list.includes(value.trim())) {
    ElMessage.warning('该标签已存在')
  }
}

// 修复：标签删除方法
const handleTagClose = (list, index) => {
  list.splice(index, 1)
}

// 下一步
const nextStep = () => {
  if (activeStep.value === 0) {
    basicFormRef.value.validate((valid) => {
      if (valid) {
        activeStep.value++
      } else {
        ElMessage.warning('请完善基础信息')
      }
    })
  } else if (activeStep.value === 1) {
    // 第二步非必填，直接下一步
    activeStep.value++
    updateAbilityTable()
  }
}

// 上一步
const prevStep = () => {
  activeStep.value--
}

// 更新能力表格数据
const updateAbilityTable = () => {
  abilityTableData.value = [
    { name: '创新能力', score: abilityForm.innovation },
    { name: '学习能力', score: abilityForm.learning },
    { name: '抗压能力', score: abilityForm.pressure },
    { name: '沟通能力', score: abilityForm.communication },
    { name: '实习能力', score: abilityForm.internship }
  ]
}

// 生成能力画像
const generateAbility = () => {
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在生成你的能力画像...',
    background: 'rgba(0, 0, 0, 0.7)'
  })

  setTimeout(() => {
    updateAbilityTable()
    activeStep.value++
    loadingInstance.close()
    ElMessage.success('能力画像生成成功！')
  }, 1500)
}

// 保存能力画像
const saveAbility = () => {
  // 整合所有信息
  const studentInfo = {
    basic: { ...basicForm },
    skill: { ...skillForm },
    ability: { ...abilityForm }
  }

  // 计算各维度得分（供匹配页使用）
  const studentAbility = {
    baseScore: 90, // 基础要求得分（固定，可根据实际逻辑调整）
    skillScore: skillForm.skills.length >= 3 ? 85 : 70, // 技能得分
    qualityScore: (abilityForm.communication + abilityForm.pressure) / 2, // 素养得分
    potentialScore: (abilityForm.innovation + abilityForm.learning) / 2 // 潜力得分
  }

  // 保存到本地存储
  localStorage.setItem('studentInfo', JSON.stringify(studentInfo))
  localStorage.setItem('studentAbility', JSON.stringify(studentAbility))

  ElMessage.success('能力画像保存成功！')
  router.push('/match-result')
}

// 重置表单
const resetForm = () => {
  activeStep.value = 0
  // 重置所有表单
  basicFormRef.value.resetFields()
  skillForm.skills = []
  skillForm.certificates = []
  skillForm.internship = ''
  skillForm.project = ''
  abilityForm.innovation = 80
  abilityForm.learning = 85
  abilityForm.pressure = 75
  abilityForm.communication = 80
  abilityForm.internship = 70
  // 重置临时输入框
  tempSkill.value = ''
  tempCert.value = ''
}
</script>

<style scoped>
.student-ability-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.ability-result {
  text-align: center;
  padding: 20px 0;
}

/* 修复：标签输入容器样式 */
.tag-input-container {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 8px;
}

:deep(.el-slider) {
  width: 80%;
  margin: 0 auto;
}
</style>