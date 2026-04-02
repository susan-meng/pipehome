# 主控 Agent 流程图（详细版：含关键子 Agent 子流程）

下面是根据 `asbot_controller_agent_d1d50401140233_知识助手.json`（主控）以及 `docs/subagent-1-simplified.json`（子 agent 配置）整理的 Mermaid 流程图。

```mermaid
flowchart TD
  A([开始]) --> B["拆分输入 $query<br/>按 '用户还上传了以下文档'<br/>→ user_query, content"]
  B --> C["intent = ''<br/>query_expansion = ''"]

  C --> D{需要进行上下文改写？}
  D -->|Y| E["@__判断是否需要进行上下文改写__1<br/>得到 answer.answer == 'Y'"]
  E --> F["@__根据上下文改写query__1<br/>得到 rewrite_query"]
  F --> G{skill 为空？}
  G -->|是| H["@__知识助手_意图识别__1<br/>intent = intent_res.answer.answer"]
  H --> I["@__query改写__1<br/>query_expansion = new_query.answer.answer（可用于后续检索/生成）"]
  G -->|否| J{"skill 是否为 __文档问答__2 或 __文件搜索__1？"}
  J -->|是| I
  J -->|否| K["跳过 query_expansion 扩写（query_expansion 可能保持为空）"]

  D -->|N| L{skill 为空？}
  L -->|是| M["@__知识助手_意图识别__1<br/>得到 intent"]
  M --> N{"intent 是否为 文档问答/找文件？"}
  N -->|是| O["@__query改写__1<br/>得到 query_expansion"]
  N -->|否| P["query_expansion 保持为空"]
  L -->|否| Q{"skill 是否为 __文档问答__2 或 __文件搜索__1？"}
  Q -->|是| O
  Q -->|否| P

  I --> R{query_expansion 为空？}
  K --> R
  O --> R
  P --> R
  R -->|是| R1["query_expansion = user_query"]
  R -->|否| R2["保留 query_expansion"]

  R1 --> S{web_search_mode == on？}
  R2 --> S

  S -->|是| T["@WebSearch(search_query=user_query)<br/>拼接 web_search_result"]
  S -->|否| U["web_search_result 为空/默认"]
  T --> V
  U --> V

  V["按 skill 优先，否则按 intent 分发"] --> W{命中哪类？}

  W -->|扩写| XA["@__全文扩写__3(query_expansion, content, as_ctx, web_search_res, contexts)"]
  W -->|总结| XB["@__文档总结__3(query_expansion, content, as_ctx, web_search_res, contexts)"]
  W -->|续写| XC["@__全文续写__3(query_expansion, content, as_ctx, web_search_res, contexts)"]
  W -->|提炼关键字| XD["@__提炼关键字__2(query_expansion, content, as_ctx, web_search_res, contexts)"]
  W -->|帮我写作| XE["@__帮我写作__2(query_expansion, content, as_ctx, web_search_res, contexts)"]
  W -->|大纲写作| XF["@__大纲写作__1(query_expansion, content, as_ctx, web_search_res, contexts)"]

  W -->|文档问答| DQA["子流程：__文档问答__2（含 content为空时的 FAQ 兜底）"]
  W -->|翻译| XG["@__文档翻译__3(query_expansion, content, as_ctx, web_search_res, contexts)"]
  W -->|全文写作| XH["@__全文写作__3(query_expansion, content, as_ctx, web_search_res, contexts)"]
  W -->|文件搜索| FS["子流程：__文件搜索__1"]
  W -->|规则审阅| XI["@__规则审阅__1(query_expansion, content, as_ctx, web_search_res, contexts)"]

  W -->|日常闲聊| XA1["/prompt/（可选带 web_search_result）"]
  W -->|其它/兜底| EL1["子流程：else 兜底（FAQ -> 文档问答 or prompt）"]

  XA --> END([结束])
  XB --> END
  XC --> END
  XD --> END
  XE --> END
  XF --> END
  XG --> END
  XH --> END
  XI --> END
  XA1 --> END
  DQA --> END
  FS --> END
  EL1 --> END

  %% ================================
  %% 子流程：__文档问答__2
  %% ================================
  subgraph DQASub["__文档问答__2 执行（详细：7个逻辑块）"]
    direction TD
    DQStart([进入 __文档问答__2])

    DQContentIsEmpty{len(content)==0?}
    DQStart --> DQContentIsEmpty

    DQContentIsEmpty -->|是| FAQBranch["调用 __faq问答__2<br/>得到 faq_ans"]
    FAQBranch --> FAQUnique{faq_ans.answer.answer.is_unique_match ?}
    FAQUnique -->|是| DQDataUniq["构造 data_source_answer（仅使用唯一匹配那一条）"]
    FAQUnique -->|否| FallbackDQ["调用 __文档问答__2（继续走召回+问答，content可能为空）"]

    DQContentIsEmpty -->|否| DQPipelineStart[走文档问答主流水线（content非空）]

    DQPipelineStart --> B1["__获取当前时间__1（function_block）"]
    B1 --> B2["预处理（LLM：从 query 提取 username/time -> new_input）"]
    B2 --> B3["文档召回（function_block：多路召回/重排/扩上下文）"]
    B3 --> B31["step1_recall（召回：doc/wiki/faq）"]
    B3 --> B32["step2_rerank（rerank + 阈值过滤）"]
    B3 --> B33["step3_build_objects（按 doc_id 聚合 Top N）"]
    B3 --> B34["step4_expand_context（fetch 扩上下文）"]

    B34 --> B4["__移除图谱召回的重复文件__2（function_block）<br/>filter_by_username_and_time + 去重 + 拼回faq/user_input"]
    B4 --> B5["__整理召回的数据结构__2（function_block）<br/>按 doc_name 分组，拼接段落内容"]
    B5 --> B6["LLM 文档问答（严格引用+图片引用+冲突处理+版本筛选规则）"]
    B6 --> B7["llm_relqs（生成 3 组递进问题/答案对）"]
    B7 --> DQReturn["返回 answer + block_answer"]

    DQDataUniq --> DQReturn
    FallbackDQ --> DQPipelineStart
  end

  %% 展开：__faq问答__2（用于 content 为空分支）
  subgraph FAQSub["__faq问答__2（function_block：唯一匹配逻辑）"]
    direction TD
    FQStart([FAQ召回入口])
    FQStart --> FQ1["step1_recall_faq（召回 FAQ slice 列表）"]
    FQ1 --> FQ2["唯一定位 find_unique_faq：<br/>字符覆盖/阈值/IQR异常值"]
    FQ2 --> FQ3{"是否唯一匹配？"}
    FQ3 -->|是| FQ4["构建唯一 FAQ 对象（step2_build_faq_objects + is_unique_match=true）"]
    FQ3 -->|否| FQ5["构建候选 FAQ 对象列表（取 Top N）"]
    FQ4 --> FQRet["返回：text + is_unique_match=true + unique_match_idx"]
    FQ5 --> FQRet["返回：text + is_unique_match=false + unique_match_idx=None"]
  end

  %% ================================
  %% 子流程：__文件搜索__1
  %% ================================
  subgraph FSSSub["__文件搜索__1（详细：5个逻辑块）"]
    direction TD
    FSStart([进入 __文件搜索__1])
    FSStart --> FS1["获取当前时间（function_block）"]
    FS1 --> FS2["预处理（LLM：提取 username/time -> is_time）"]
    FS2 --> FS3["retrievers_block（检索/召回：返回 retrievers_block_content1）"]
    FS3 --> FS4["移除图谱召回的重复文件（function_block）<br/>filter_by_username_and_time + 去重 + 仅保留近窗口 + 拼faq/user_input"]
    FS4 --> FS5["LLM 格式化输出（按版本筛选/排序 + 输出推荐文档列表）"]
    FS5 --> FSRet["返回 answer + block_answer"]
  end

  %% ================================
  %% 子流程：else 兜底
  %% ================================
  subgraph ELSub["else 兜底（content为空：FAQ -> data_source_answer；否则走 prompt）"]
    direction TD
    ELStart([进入 else 兜底])
    ELStart --> ELc{len(content)==0?}
    ELc -->|是| ELa["调用 __faq问答__2 -> faq_ans"]
    ELa --> ELu{faq unique match ?}
    ELu -->|是| ELD["data_source_answer=唯一匹配那条（同 doc问答兜底逻辑）"]
    ELu -->|否| ELF["调用 __文档问答__2（即使 content 为空也继续）"]
    ELc -->|否| ELp{web_search_mode==on?}
    ELp -->|是| ELpb["/prompt/（web_search_result + content + 图片引用规则）"]
    ELp -->|否| ELps["/prompt/（仅 content + 图片引用规则）"]
    ELD --> ELRet["返回 answer"]
    ELF --> ELRet
    ELpb --> ELRet
    ELps --> ELRet
  end

  %% 注：子流程通过“调用节点”体现在上层连线中，无需再额外把主图连到 subgraph 名称。
```

