# from db import get_db

# def reset_all_tables():
#     conn = get_db()
#     cursor = conn.cursor()

#     # 清空所有可能含有数据的表（按外键依赖顺序，先删除子表）
#     tables_to_clear = [
#         'job_tags',           # 依赖 job_categories
#         'job_relations',      # 独立表，但建议清空
#         'job_profile',        # 独立表
#         'match_history',
#         'report_history',
#         'content',
#         'learning_resources',
#         'mentors',
#         'path_stage_templates',
#         'path_types',
#         'plan_goals',
#         'plan_milestones',
#         'plan_stages',
#         'user_plans',
#         'practices',
#         'reports',
#         'user_interests',
#         'user_profiles',
#         'ability_assessments',
#         'verification_codes',
#         'job_categories',     # 最后删除父表
#     ]

#     for table in tables_to_clear:
#         try:
#             cursor.execute(f"DELETE FROM {table}")
#             print(f"✅ 已清空表: {table}")
#         except Exception as e:
#             print(f"⚠️ 清空表 {table} 失败: {e}")

#     # 重置 job 表的 category_id 字段为 NULL
#     try:
#         cursor.execute("UPDATE job SET category_id = NULL")
#         print("✅ 已重置 job 表的 category_id 字段")
#     except Exception as e:
#         print(f"⚠️ 重置 job 表的 category_id 失败: {e}")

#     conn.commit()
#     conn.close()
#     print("🎉 数据库重置完成！")

# if __name__ == "__main__":
#     reset_all_tables()