# 自动补全功能使用指南

> **Language**: [中文](auto_completion.zh.md) | [English](auto_completion.en.md)

## 概述

`auto_completion` 功能为面试答案提供智能补全建议。它通过分析部分输入，基于 FAANG 面试标准生成最多 3 个推荐的补全选项，帮助候选人完成自我介绍和行为面试问题（BQ）答案。

### 核心特点

1. **智能完整性检测**：自动检测输入是否结构完整（有明确的结尾）或内容完整（覆盖所有必需元素）
2. **上下文感知建议**：根据特定职位、公司和面试级别生成量身定制的补全建议
3. **符合 FAANG 标准**：所有建议都遵循 FAANG 面试最佳实践
4. **支持两种场景**：
   - 自我介绍补全
   - 行为面试问题（BQ）答案补全
5. **前 3 名推荐**：提供最相关的补全选项及解释说明

---

## 工作原理

### 补全流程

```
用户输入（部分文本）
   ↓
检查是否结构完整（有明确结尾）？
   ├─ 是 → 返回 is_complete: true ✅
   └─ 否 → 检查内容完整性
       ├─ 所有元素齐全 → 返回 is_complete: true ✅
       └─ 缺少元素 → 生成前 3 名补全建议
           ↓
        返回带原因和置信度的建议
```

### 完整性检测逻辑

系统采用**双优先级**方法：

1. **优先级 1：结构完整性**
   - 检查最后一句是否明确表示答案已结束
   - 识别结尾短语，如："谢谢"、"我期待..."、"总之"、"总的来说"等
   - 如果结构完整 → 立即返回 `is_complete: true`
   - 建议进行评估以确保覆盖所有关键元素

2. **优先级 2：内容完整性**
   - 对于自我介绍：检查背景、经历、成就、动机、关联性
   - 对于 BQ 答案：检查 STAR 元素（Situation, Task, Action, Result）以及级别特定要求
   - 如果所有元素齐全 → 返回 `is_complete: true`

### 关键组件

1. **`AutoCompletionEngine` 类**（位于 `advance/auto_completion.py`）
   - 生成补全建议的主引擎
   - 处理自我介绍和 BQ 答案两种场景
   - 使用 LLM 进行分析和生成建议

2. **补全建议**
   - 最多 3 个推荐补全选项
   - 每个选项包括：
     * `text`：补全文本
     * `reason`：推荐此补全的原因
     * `confidence`：置信度（0-100%）

3. **响应格式**
   - 返回 JSON 对象，包含：
     * `is_complete: true` + `message`（如果完整）
     * `is_complete: false` + `completions` 数组（如果不完整）

---

## 使用方式

### 前置条件

1. **安装依赖**
   - 确保已安装所有必需的 Python 包（见 `requirements.txt`）
   - 需要 `litellm` 来访问 LLM

2. **环境设置**
   - 如需要，在 `.env` 文件中设置 API 密钥

### 基本用法

#### 示例 1：自我介绍补全

```python
import asyncio
from advance.auto_completion import AutoCompletionEngine

async def main():
    engine = AutoCompletionEngine()
    
    partial_text = """你好，我是 John，是一名有 5 年经验的软件工程师。 
    我参与过多个涉及分布式系统和微服务的项目。"""
    
    result = await engine.complete_self_intro(
        partial_text=partial_text,
        role="高级软件工程师",
        company="Google"
    )
    
    if result.get("is_complete"):
        print(f"✅ {result['message']}")
    else:
        print("📝 补全建议：")
        for i, comp in enumerate(result.get("completions", []), 1):
            print(f"\n{i}. {comp['text']}")
            print(f"   原因：{comp['reason']}")

asyncio.run(main())
```

#### 示例 2：BQ 答案补全

```python
import asyncio
from advance.auto_completion import AutoCompletionEngine

async def main():
    engine = AutoCompletionEngine()
    
    question = "告诉我你最具挑战性的项目。"
    partial_text = """我领导团队将单体应用迁移到微服务架构。
    挑战在于我们必须在保持 99.9% 正常运行时间且不中断用户的情况下完成迁移。
    
    我的任务是设计和执行零停机迁移策略。"""
    
    result = await engine.complete_bq_answer(
        partial_text=partial_text,
        question=question,
        role="高级软件工程师",
        level="Senior"
    )
    
    if result.get("is_complete"):
        print(f"✅ {result['message']}")
    else:
        print("📝 补全建议：")
        for i, comp in enumerate(result.get("completions", []), 1):
            print(f"\n{i}. {comp['text']}")
            print(f"   原因：{comp['reason']}")

asyncio.run(main())
```

### API 参考

#### `AutoCompletionEngine`

**初始化**

```python
engine = AutoCompletionEngine(model="gpt-4o-mini")
```

**参数：**
- `model` (str, 可选)：要使用的 LLM 模型。默认：`"gpt-4o-mini"`

#### `complete_self_intro()`

为自我介绍生成补全建议。

```python
async def complete_self_intro(
    partial_text: str,
    role: str = "Software Engineer",
    company: str = "FAANG"
) -> Dict[str, Any]
```

**参数：**
- `partial_text` (str, 必需)：部分自我介绍文本
- `role` (str, 可选)：职位。默认：`"Software Engineer"`
- `company` (str, 可选)：公司名称。默认：`"FAANG"`

**返回：**
- `Dict[str, Any]`：JSON 对象，包含：
  - `{"is_complete": true, "message": "..."}` 如果完整
  - `{"is_complete": false, "completions": [...]}` 如果不完整

#### `complete_bq_answer()`

为 BQ 答案生成补全建议。

```python
async def complete_bq_answer(
    partial_text: str,
    question: str,
    role: str = "Software Engineer",
    level: str = "Senior"
) -> Dict[str, Any]
```

**参数：**
- `partial_text` (str, 必需)：部分 BQ 答案文本
- `question` (str, 必需)：行为面试问题
- `role` (str, 可选)：职位。默认：`"Software Engineer"`
- `level` (str, 可选)：候选人级别。默认：`"Senior"`。选项：`"Junior-Mid"`, `"Senior"`, `"Staff"`

**返回：**
- `Dict[str, Any]`：JSON 对象，包含：
  - `{"is_complete": true, "message": "..."}` 如果完整
  - `{"is_complete": false, "completions": [...]}` 如果不完整

#### `complete()`（通用方法）

两种场景的通用方法。

```python
async def complete(
    scenario: Literal["self-intro", "bq answer"],
    partial_text: str,
    role: str = "Software Engineer",
    company: str = "FAANG",
    question: Optional[str] = None,
    level: str = "Senior"
) -> Dict[str, Any]
```

**参数：**
- `scenario` (str, 必需)：`"self-intro"` 或 `"bq answer"`
- `partial_text` (str, 必需)：部分文本输入
- `role` (str, 可选)：职位
- `company` (str, 可选)：公司名称（用于自我介绍）
- `question` (str, 可选)：BQ 问题（`"bq answer"` 场景必需）
- `level` (str, 可选)：候选人级别（用于 BQ 答案）

---

## 响应格式

### 完整响应

当输入完整时：

```json
{
  "is_complete": true,
  "message": "您的自我介绍已经完整且优秀。"
}
```

### 不完整响应

当输入需要补全时：

```json
{
  "is_complete": false,
  "reason": "为什么介绍已完成或未完成",
  "confidence": "85%",
  "completions": [
    {
      "text": "补全选项 1",
      "reason": "推荐此选项的原因",
      "confidence": "90%"
    },
    {
      "text": "补全选项 2",
      "reason": "推荐此选项的原因",
      "confidence": "85%"
    },
    {
      "text": "补全选项 3",
      "reason": "推荐此选项的原因",
      "confidence": "80%"
    }
  ]
}
```

### 错误响应

如果 JSON 解析失败：

```json
{
  "is_complete": false,
  "error": "解析 LLM 响应为 JSON 失败：...",
  "raw_response": "原始 LLM 响应文本"
}
```

---

## 最佳实践

### 对于自我介绍

1. **包含关键元素**：
   - 背景和经验水平
   - 相关工作经历
   - 关键成就（带指标）
   - 对职位/公司的动机
   - 与职位/公司的关联性

2. **保持简洁**：目标是在口述时 1-2 分钟

3. **具体化**：使用具体示例和指标

4. **明确结尾**：使用结尾短语表示完成

### 对于 BQ 答案

1. **遵循 STAR 方法**：
   - **Situation（情况）**：清晰的背景和上下文
   - **Task（任务）**：具体的挑战或目标
   - **Action（行动）**：详细的行动，明确所有权
   - **Result（结果）**：可衡量的成果和影响

2. **级别特定要求**：
   - **Junior-Mid**：关注清晰度和结构化思维
   - **Senior**：展示所有权、跨职能协作、执行力
   - **Staff**：展示影响力、多团队策略、系统性思维

3. **包含指标**：始终包含可量化的结果

4. **展示所有权**：使用"我"的陈述，不仅仅是"我们"

5. **添加反思**：在适当时包含学习成果

---

## 示例

查看 `examples/auto_completion_example.py` 获取完整的工作示例，包括：

1. 使用部分输入进行自我介绍补全
2. 使用 STAR 结构进行 BQ 答案补全
3. 使用完整答案进行测试（应返回 `is_complete: true`）

---

## 故障排除

### 常见问题

1. **JSON 解析错误**
   - 系统使用正则表达式从 LLM 响应中提取 JSON
   - 如果解析失败，检查错误输出中的 `raw_response` 字段
   - LLM 应根据提示输出有效的 JSON

2. **未生成补全建议**
   - 检查输入是否已完整（返回 `is_complete: true`）
   - 确保输入确实不完整（不仅仅是简短）

3. **建议质量低**
   - 尝试在 `partial_text` 中提供更多上下文
   - 指定正确的 `role` 和 `level` 参数
   - 确保输入遵循面试答案结构

---

## 集成

### CLI 集成

您可以通过添加新命令将此功能集成到 CLI 中：

```python
# 在 cli.py 中
from advance.auto_completion import AutoCompletionEngine

async def auto_complete_command(scenario, text, **kwargs):
    engine = AutoCompletionEngine()
    result = await engine.complete(scenario, text, **kwargs)
    return result
```

### Web API 集成

对于 Web API 集成，创建端点：

```python
# 在 app.py 中
from advance.auto_completion import AutoCompletionEngine

@app.post("/api/auto-complete")
async def auto_complete(
    scenario: str,
    partial_text: str,
    role: str = "Software Engineer",
    company: str = "FAANG",
    question: Optional[str] = None,
    level: str = "Senior"
):
    engine = AutoCompletionEngine()
    result = await engine.complete(
        scenario=scenario,
        partial_text=partial_text,
        role=role,
        company=company,
        question=question,
        level=level
    )
    return result
```

---

## 技术细节

### LLM 模型

- 默认模型：`gpt-4o-mini`
- 可通过 `AutoCompletionEngine(model="...")` 自定义
- 使用流式传输以获得更好的性能

### JSON 提取

- 使用正则表达式模式 `r"\{[\s\S]*\}"` 从响应中提取 JSON
- 处理 LLM 在 JSON 前后添加额外文本的情况
- 如果未找到 JSON 块，则回退到解析整个响应

### 错误处理

- 捕获 `JSONDecodeError` 并返回错误信息
- 保留 `raw_response` 用于调试
- 返回结构化错误响应而不是引发异常

---

## 相关功能

- **自我改进**：使用 `advance/self_improve.py` 迭代改进答案
- **故事构建器**：使用 `advance/story_builder.py` 从头构建 BQ 故事
- **面试分析器**：使用 `interview_analyzer.py` 分析完整答案

---

## 支持

如有问题或疑问：
1. 查看 `examples/auto_completion_example.py` 中的示例
2. 查看 `prompts.py` 中的提示模板（类 `AutoCompletion`）
3. 检查 `error` 和 `raw_response` 字段中的错误消息

