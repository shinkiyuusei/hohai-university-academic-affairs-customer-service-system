<template>
  <div class="academic-policy-management">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon class="title-icon"><Document /></el-icon>
        教务政策管理
      </h1>
      <p class="page-subtitle">
        管理教务相关政策文档和规定
      </p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="left-actions">
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加政策
        </el-button>
      </div>
      <div class="right-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索政策标题或内容"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 政策列表 -->
    <el-table
      :data="policyList"
      :loading="loading"
      style="width: 100%"
      row-key="id"
    >
      <el-table-column prop="policy_name" label="政策名称" width="200" />
      <el-table-column prop="policy_type" label="政策类型" width="120" />
      <el-table-column prop="effective_date" label="生效日期" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'warning'">
            {{ row.status === 1 ? '生效' : '失效' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="summary" label="摘要" show-overflow-tooltip />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="viewPolicy(row)">
            <el-icon><View /></el-icon>
            查看
          </el-button>
          <el-button type="primary" link @click="editPolicy(row)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button type="danger" link @click="deletePolicy(row.id)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      class="pagination"
    />
  </div>
</template>
