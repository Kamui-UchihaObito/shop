# 电商运营部辅助型智能体（Agent）

> 面向公司 **产品运营部** 的**辅助型（非替代型）**智能体：整合知识检索（SOP/制度/模板/案例）、日常工作检索（Owner/归口/历史记录）、评论洞察（情感/方面/主题）、优缺点总结与可执行改进建议，帮助新人快速上手，辅助资深同学提效与决策。

## 目录
- [快速开始](#快速开始)
- [系统架构](#系统架构)
- [核心能力](#核心能力)
- [模块说明](#模块说明)
- [数据与知识库](#数据与知识库)
- [开发与运行](#开发与运行)
- [评估与监控](#评估与监控)
- [安全与合规](#安全与合规)
- [Roadmap](#roadmap)
- [FAQ](#faq)
- [贡献指南](#贡献指南)
- [License](#license)

---

## 快速开始

### 1) 环境准备
> 推荐使用你已创建的 Conda 环境 `shop`。

```bash
# 创建/激活环境（若已存在直接激活）
conda create -n shop python=3.10 -y
conda activate shop

# 基础依赖（按需精简/增补）
pip install -U \
  fastapi uvicorn[standard] pydantic python-dotenv \
  langchain langchain-community langchain-text-splitters \
  httpx tiktoken openai \
  sentencepiece transformers accelerate \
  pydantic-settings loguru \
  pandas numpy scikit-learn \
  jieba rich tqdm

# 选配：向量库（择一）
pip install -U chromadb          # 轻量本地
# 或
pip install -U pymilvus          # 接入 Milvus
# 或
pip install -U qdrant-client     # 接入 Qdrant

# 选配：评测/可视化
pip install -U matplotlib evaluate rouge-score nltk
```

> **GPU/大模型推理**：如需本地推理，按显卡安装 `torch`/`cuda` 版本及相应推理库（如 vLLM/ollama/AutoAWQ 等），本文档以 API 调用为主。

### 2) 配置
在项目根目录创建 `.env`（或 `config/.env`）：
```bash
# LLM / Embedding
OPENAI_API_KEY=sk-***
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini    # 示例；按需替换

# 向量库（任选一种）
VECTOR_DB=chromadb          # chromadb | milvus | qdrant

# Milvus / Qdrant 连接（如使用）
MILVUS_HOST=localhost
MILVUS_PORT=19530
QDRANT_HOST=localhost
QDRANT_PORT=6333

# 项目
PROJECT_NAME=ops-assistant
ENV=dev
```

### 3) 目录结构建议
```
.
├─ agent/                 # Agent 逻辑（路由、规划、工具、记忆）
│  ├─ router.py
│  ├─ planner.py
│  ├─ tools/
│  ├─ memory/
│  └─ prompts/
├─ rag/                   # 检索增强（索引、嵌入、重排）
│  ├─ ingest.py
│  ├─ retriever.py
│  ├─ reranker.py
│  └─ schemas.py
├─ voc/                   # 评价解析（情感、方面、主题、建议）
│  ├─ sentiment.py
│  ├─ aspect_mining.py
│  ├─ keywords.py
│  └─ summarizer.py
├─ data/                  # 原始/清洗数据（本地仅示例，生产用对象存储）
├─ docs/                  # SOP/制度/模板/案例等原始文档
├─ api/                   # FastAPI 服务
│  ├─ main.py
│  └─ schemas.py
├─ configs/               # YAML/ENV 配置
├─ scripts/               # 任务脚本（批处理/定时）
└─ tests/                 # 单元/集成/回归测试
```

### 4) 文档入库（RAG 索引）
```bash
# 将 docs/ 下 SOP、制度、模板、案例等切分并向量化入库
python rag/ingest.py --source ./docs --db ${VECTOR_DB:-chromadb}
```

### 5) 启动服务
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
# 访问: http://localhost:8000/docs
```

---

## 系统架构

```
          ┌──────────────────────────────────────────────────────┐
          │                      用户（运营同学/新人）             │
          └───────────────▲───────────────────────────▲──────────┘
                          输入                          上下文
                          │                             │
┌─────────────────────────┴─────────────────────────────┴────────────────────┐
│                                Agent Orchestrator                          │
│  (Router/Planner → Tool-Use/Reasoning → Judge/Verifier → Answer Synthesis) │
└───────▲───────────────▲───────────────▲──────────────▲───────────────▲────┘
        │               │               │              │               │
        │               │               │              │               │
   ┌────┴───┐      ┌────┴───┐      ┌────┴───┐     ┌───┴────┐     ┌────┴────┐
   │ RAG检索│      │ VOC分析│      │知识检索│     │模板检索│     │数据查询│
   │(Retriever│    │(情感/方面│   │(SOP/制度│     │(OKR/表单│     │(SQL/指标│
   │  +Rerank)│    │  关键词)│   │  案例)   │     │  模板) │     │  画像)  │
   └────┬───┘      └────┬───┘      └────┬───┘     └───┬────┘     └────┬────┘
        │                │               │              │               │
        ▼                ▼               ▼              ▼               ▼
  向量库/索引        情感/方面模型     文档库/知识库    模板库/资产库     数据仓库/指标口径
 (Chroma/Milvus/       (本地/API)      (文件+元数据)   (表单/文档)        (SQL/缓存)
   Qdrant)
```

---

## 核心能力

1. **意图识别（一级/二级）**  
   - 一级：知识检索、SOP 问答、日常工作检索、VOC 分析、模板生成、数据查询等。  
   - 二级：在“法律/电商”等跨域或多标签场景，采用**多标签分类 + 置信度阈值 + 回退策略**（不强制单域）。

2. **RAG 检索与答案生成**  
   - 文档切分（规则/语义）、嵌入、向量召回、可选 **Rerank**、引用标注与可追溯来源。  
   - 支持多库（Chroma/Milvus/Qdrant），可扩展 ES/OpenSearch 关键词检索混排。

3. **VOC 评论洞察**  
   - 情感（正/负/中）、方面-情感对、主题/关键词、Top 痛点与亮点、可执行改进建议。  
   - 输出结构化摘要（面向运营报告/复盘）。

4. **新人入职与日常检索**  
   - SOP/制度/模板/Owner/归口，一问即得；提供“下一步怎么做”的操作化建议与链接。

5. **任务化回答**  
   - Agent 内置 Planner（规划）与 Tool-Use（工具调用），输出**步骤化清单**（Check List）。

---

## 模块说明

### Router（路由）
- 基于轻量分类模型或 LLM 判别策略，决定调用链路：RAG、VOC、模板、数据查询等。
- 产出：`{intent: str, confidence: float, slots: {...}}`。

### Planner（规划）
- 将复杂请求拆解为子任务（ReAct/Plan→Do→Check），并选择工具序列。
- 支持失败重试与**最低可行回答**（Partial Answer）策略。

### Tools（工具层）
- **rag.search**：从向量库检索、可选 Rerank。  
- **voc.analyze**：评论情感/方面抽取、聚合与总结。  
- **kb.lookup**：SOP/制度/案例/模板精确检索（关键词 + 向量混合）。  
- **sql.query**：数据仓/指标查询（含口径说明）。  
- **template.fill**：根据槽位填充内部模板（通知、复盘、日报、PRD 骨架等）。

> 工具均通过统一 `ToolSpec` 描述入参/出参与异常。

### Memory（会话记忆）
- 短期：当前会话摘要与已使用来源。  
- 可选长期：保存个人偏好（如“回答优先中文，返回行动清单”）。

### Judge/Verifier（答案校验）
- 引用率检查、来源覆盖度、是否存在幻觉（Heuristic+LLM 交叉）。  
- 不足时自动追加检索或降级为“可行的部分答案 + TODO”。

---

## 数据与知识库

### 文档类型
- **SOP/制度/流程**、**模板/表单**、**历史案例/复盘**、**术语与口径**。  
- 统一抽取元数据：`{部门, 归口, 版本, 生效日期, 标签, 来源URL/路径}`。

### 索引策略
- 切分：按标题/小节/句段，结合中文断句与语义分段。  
- 嵌入：中文向量模型或 API（按可用性与合规选型）。  
- Rerank（可选）：提升长文命中质量（如 Cross-Encoder）。

### VOC 数据
- 原始表：`user_evaluation_reviews_raw.csv`  
- 清洗表：`user_evaluation_reviews_clean.csv`  
- 丢弃表：`user_evaluation_reviews_dropped.csv`  
- 字段建议：`{review_id, product_id, sku, content, rating, ts, attributes, source}`

---

## 开发与运行

### API 约定（FastAPI 示例）

**请求**
```json
POST /v1/agent/ask
{
  "query": "新人入职第一周需要完成哪些任务？有没有模板？",
  "context": {"user_role": "product-ops", "language": "zh"},
  "options": {"need_refs": true}
}
```

**响应**
```json
{
  "answer": "…（带步骤清单与可执行建议）…",
  "refs": [
    {"title": "产品运营新人7日SOP", "uri": "docs/sop/onboarding.md", "chunk_id": "…"}
  ],
  "trace": {
    "intent": "SOP_ASK",
    "tools": ["rag.search", "template.fill"],
    "latency_ms": 1432
  }
}
```

### 关键脚本

**文档入库**
```bash
python rag/ingest.py \
  --source ./docs \
  --db chromadb \
  --chunk-size 800 --chunk-overlap 120 \
  --meta "dept=ops,tags=onboarding,sop=1"
```

**批量 VOC 解析**
```bash
python voc/sentiment.py --input data/user_evaluation_reviews_clean.csv \
                        --output data/voc_sentiment.jsonl
python voc/aspect_mining.py --input data/user_evaluation_reviews_clean.csv \
                            --output data/voc_aspects.jsonl
python voc/summarizer.py --sent data/voc_sentiment.jsonl \
                         --aspect data/voc_aspects.jsonl \
                         --out data/voc_report.md
```

### 最小示例（RAG 检索 → 生成）
```python
# api/snippets/min_rag.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnableMap, RunnablePassthrough

# 1) 载入/切分
docs = ["...加载 docs/ 中的文本..."]
spl = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
chunks = spl.create_documents(docs)

# 2) 向量化与索引
vs = Chroma.from_documents(chunks, OpenAIEmbeddings())

# 3) 构建链路
retriever = vs.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-4o-mini")

def synthesize(inputs):
    ctx = "\n\n".join([d.page_content for d in inputs["docs"]])
    q = inputs["question"]
    prompt = f"已知内容：\n{ctx}\n\n问题：{q}\n请用中文回答，并在末尾列出引用小标题。"
    return llm.invoke(prompt).content

chain = RunnableMap({
    "question": RunnablePassthrough(),
    "docs": retriever
}).assign(answer=synthesize)

print(chain.invoke("新人第一周要做什么？")["answer"])
```

---

## 评估与监控

### 召回/排序指标
- **Recall@k**、**MRR**（Mean Reciprocal Rank）验证检索质量。  
- **命中可解释性**：引用段落应覆盖回答关键句。

### 生成质量
- **ROUGE**（文本覆盖/召回）、**BLEU**（n-gram 精准度）用于模板化回答/摘要的稳定性趋势对比。  
- 人评维度：**正确性、完整性、可执行性、来源可信度**。

### 离线评测集
- 构建 `eval/`：包含 **Query → 参考答案/参考来源**。  
- 定期跑基准，回归监控（如每周）。

### 在线监控
- 记录：意图分布、工具调用次数、回答时长 P50/P95、失败率、无答案率。  
- 采样人工抽检与“低置信度二次确认”流程。

---

## 安全与合规

- **权限与可见性**：不同组仅能访问其有权的知识分库与数据口径。  
- **引用标注**：默认开启，便于追溯。  
- **敏感信息**：脱敏/模糊化处理；日志不落敏感内容。  
- **Hallucination 缓解**：低置信度时降级为“检索结果 + 人工待确认”。

---

## Roadmap

- [ ] 多租户与细粒度权限（Owner/归口/标签级）  
- [ ] 文档增量入库与版本追踪（生效/废止）  
- [ ] VOC 方面-情感对的可视化看板与时序对比  
- [ ] 数据查询口径对齐（字典化与可视化 Explain）  
- [ ] Reranker 引入与可学习路由（Contextual Bandit）  
- [ ] 新人任务清单自动生成 + 日报周报模板一键填充

---

## FAQ

**Q1：为何不用“全量微调”，而采用 RAG + 轻量模块？**  
A：知识频繁变更，RAG 可即时更新；必要时对意图分类器、重排器或情感模型做 **LoRA/SFT/QLoRA** 迭代，成本更低。

**Q2：跨法域/跨标签如何处理？**  
A：多标签分类 + 召回合并 + Rerank，保持召回覆盖后由判别器/规则做最终裁决。

**Q3：如何减少幻觉？**  
A：强制引用、答案后置校验、低置信度降级；必要时返回“部分答案 + 待确认项”。

---

## 贡献指南

1. 新建分支：`feature/<module-name>`  
2. 为模块补充 **类型注解/单元测试/文档**；PR 模板需填写：变更点、影响面、回滚方案。  
3. 通过 CI（lint、tests、简单基准）后合并。

---

## License

内部项目，默认**仅限公司内部使用**。若需外部发布，请在法务评审后调整许可条款。

---
