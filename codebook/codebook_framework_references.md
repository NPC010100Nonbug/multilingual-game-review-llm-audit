# Codebook 构建框架参考资料

**项目**：Multilingual Game Review LLM Audit / Training Project  
**研究对象**：中、英、日 Steam 评论中的 `perceived unfairness`  
**文档状态**：参考资料清单，不是已经冻结的正式 codebook  
**整理日期**：2026-08-05

## 1. 本文档的用途

目前没有找到可以直接照搬的“多语言 Steam 游戏评论 perceived unfairness”成熟 codebook。本项目需要组合三类证据：

1. **构念来源**：回答“什么是 fairness / unfairness，以及它不同于什么”。
2. **游戏语境来源**：回答“不公平在游戏、竞争、匹配、技术条件和商业化中如何表现”。
3. **标注工程来源**：回答“标签定义、正反例、证据片段、置信度、分歧和版本控制应如何记录”。

GitHub 仓库和其他数据集的 annotation guidelines 只能作为结构模板，不能替代构念效度证据。游戏商业化论文也只能覆盖整体构念的一部分，不能把所有高价、困难、bug 或负面体验自动定义为不公平。

## 2. 优先阅读顺序

| 优先级 | 来源 | 主要用途 |
|---|---|---|
| 1 | Petrovskaya, Deterding, & Zendle (2022) + OSF codebooks | 最接近可直接检查的游戏评论 codebook 实物 |
| 2 | Freeman et al. (2022) | 竞技游戏中 fairness、P2W、技能、匹配和商业化的直接研究 |
| 3 | Colquitt (2001)；Xia et al. (2004) | 总体 justice 维度和 price fairness 边界 |
| 4 | Petrovskaya & Zendle (2022) | 玩家认为不公平、误导或侵略性的商业化机制分类 |
| 5 | MFRC / MFTC；Complaints；CAD；Social Bias Frames | codebook 的显式/隐式、负例、证据 span、解释字段和困难案例结构 |
| 6 | MacQueen et al. (1998)；DeCuir-Gunby et al. (2011) | codebook entry 本身的字段模板（含 inclusion / exclusion） |
| 7 | Röttger et al. (2021)（HateCheck） | 对照式硬负例与 minimal pair 的构造方式 |
| 8 | Röttger et al. (2022)；Davani et al. (2022)；O'Connor & Joffe (2020)；Hershcovich et al. (2022) | 主观标注范式、分歧处理、可靠性方法与跨文化适配 |

## 3. 构念定义与理论基础

### 3.1 Colquitt (2001)：四维 justice 框架

**Reference**  
Colquitt, J. A. (2001). On the dimensionality of organizational justice: A construct validation of a measure. *Journal of Applied Psychology, 86*(3), 386–400. https://doi.org/10.1037/0021-9010.86.3.386

**可借用内容**

- `distributive justice`：结果、资源、机会或负担的分配是否公平。
- `procedural justice`：产生结果的程序是否公平。
- `interpersonal justice`：相关方是否受到尊重、有尊严的对待。
- `informational justice`：是否提供充分、诚实、合理的解释和信息。

**本项目边界**

- 原始研究场景是组织管理，而不是游戏或消费者评论。
- 适合作为上层维度来源，不能宣称四维结构已经在 Steam 评论上获得验证。

### 3.2 Leventhal (1980)：程序公平标准

**Reference**  
Leventhal, G. S. (1980). What should be done with equity theory? New approaches to the study of fairness in social relationships. In K. J. Gergen, M. S. Greenberg, & R. H. Willis (Eds.), *Social Exchange: Advances in Theory and Research* (pp. 27–55). Springer. https://doi.org/10.1007/978-1-4613-3087-5_2

**可借用内容**

- 程序的一致性。
- 避免偏见。
- 依据准确信息。
- 允许纠正错误。
- 考虑相关方利益与意见。
- 符合伦理标准。

**潜在游戏映射**：匹配、RNG、封禁、退款、申诉、补丁和社区治理。

**本项目边界**：只有评论文本实际表达或清楚暗示相关规范时才能标注，不能由标注者替评论者补充理论推断。

### 3.3 Xia, Monroe, & Cox (2004)：price fairness

**Reference**  
Xia, L., Monroe, K. B., & Cox, J. L. (2004). The price is unfair! A conceptual framework of price fairness perceptions. *Journal of Marketing, 68*(4), 1–15. https://doi.org/10.1509/jmkg.68.4.1.42733

**可借用内容**

- 价格公平是一种消费者判断：价格差异或交易条件是否合理、可接受或可正当化。
- 公平判断通常依赖比较对象、参照交易、规范或应得关系。
- 不满意、低价值和不公平不是同一个概念。

**本项目边界**：`too expensive`、`not worth it` 或 `价格太高` 本身不能自动成为 `PRESENT`。

### 3.4 Kahneman, Knetsch, & Thaler (1986)：reference transaction 与 entitlement

**Reference**  
Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1986). Fairness as a constraint on profit seeking: Entitlements in the market. *American Economic Review, 76*(4), 728–741. [Princeton author copy](https://kahneman.scholar.princeton.edu/document/10)

**可借用内容**

- 人们会以既有价格、近期交易、竞争者条件或稳定惯例作为公平判断的参照点。
- 当企业利用市场力量破坏已形成的合理期待时，消费者可能形成不公平判断。

**本项目边界**：稳定或常见的做法并不必然在规范上正当；本项目记录评论者的 perception，而不是确认企业行为客观不公。

### 3.5 Bolton, Warlop, & Alba (2003)：消费者 price unfairness 的归因

**Reference**  
Bolton, L. E., Warlop, L., & Alba, J. W. (2003). Consumer perceptions of price (un)fairness. *Journal of Consumer Research, 29*(4), 474–491. https://doi.org/10.1086/346244

**可借用内容**

- 消费者会参考过去价格、竞争者价格和对卖方成本的估计。
- 消费者的成本与利润推断可能不准确。

**本项目边界**：`perceived unfairness` 标签不能被解释为开发者实际存在欺骗或剥削的事实证据。

### 3.6 Zeithaml (1988)：perceived value 不是 unfairness

**Reference**  
Zeithaml, V. A. (1988). Consumer perceptions of price, quality, and value: A means-end model and synthesis of evidence. *Journal of Marketing, 52*(3), 2–22. https://doi.org/10.1177/002224298805200302

**可借用内容**

- Perceived value 是对“所得”与“所付”的总体效用评价。
- 可用于建立 hard negative：低质量、低价值或价格高不必然构成公平规范被违反。

### 3.7 Mikula, Petri, & Tanzer (1990)：日常 injustice 经验

**Reference**  
Mikula, G., Petri, B., & Tanzer, N. (1990). What people regard as unjust: Types and structures of everyday experiences of injustice. *European Journal of Social Psychology, 20*(2), 133–149. https://doi.org/10.1002/ejsp.2420200205

**可借用内容**

- 日常不公经验不仅涉及结果和程序，也可能涉及受到怎样的对待。
- 提醒项目不要把 unfairness 缩减成纯数值平衡问题。

### 3.8 Smith, Bolton, & Wagner (1999)；Blodgett, Hill, & Tax (1997)：感知不公正与抱怨行为

**Reference**  
Smith, A. K., Bolton, R. N., & Wagner, J. (1999). A model of customer satisfaction with service encounters involving failure and recovery. *Journal of Marketing Research, 36*(3), 356–372. https://doi.org/10.1177/002224379903600305

Blodgett, J. G., Hill, D. J., & Tax, S. S. (1997). The effects of distributive, procedural, and interactional justice on postcomplaint behavior. *Journal of Retailing, 73*(2), 185–210. https://doi.org/10.1016/S0022-4359(97)90003-8

**可借用内容**

- 把 Colquitt 的组织场景 justice 维度迁移到**消费者—企业**场景，形成 `distributive / procedural / interactional` 三维。
- 提供本项目缺失的一条理论链路：**感知到不公正是抱怨行为（negative word-of-mouth）的前因**。Steam 差评本身就是 negative word-of-mouth，因此语料的产生机制与该文献的因变量同构。
- Blodgett 等发现 interactional justice 对负面口碑影响最大，可支持本项目保留 `interpersonal` 子类（客服、官方回应、封禁沟通），而不是只标数值与机制。

**本项目边界**

- 两篇研究的场景是零售/服务补救，`service failure → recovery → 再评价` 的三段结构在 Steam 评论中通常不完整，多数评论只呈现失败而没有补救环节。
- 该文献用量表测 perception，本项目从**非诱发的自然文本**中推断 perception，二者不可直接等同；不能用其效应量为本项目的 prevalence 背书。

## 4. 游戏语境中的公平与不公平

### 4.1 Freeman et al. (2022)：竞技游戏内购买公平

**Reference**  
Freeman, G., Wu, K., Nower, N., & Wohn, D. Y. (2022). Pay to win or pay to cheat: How players of competitive online games perceive fairness of in-game purchases. *Proceedings of the ACM on Human-Computer Interaction, 6*(CHI PLAY), Article 247. https://doi.org/10.1145/3549510

**Author PDF**：https://guof.people.clemson.edu/papers/chiplay22.pdf

**可借用内容**

- Balanced / unbalanced gameplay。
- Functional purchases 不必然不公平。
- 玩家与开发者之间的信任。
- 技能、韧性和策略在获胜机会中的作用。
- P2W、overpowered purchases、coerced purchases、pay-or-grind、lack of fair value。
- Unfair matchmaking 与资源获取机会差异。
- 先用小样本迭代 codebook，再独立编码的开发流程。

**本项目边界**

- 研究集中于五款竞技体育/卡牌游戏和 Reddit。
- 不能直接覆盖 Elden Ring 等单人/PvE 场景的机制公平。
- 该研究的简单 agreement 不能替代本项目预先规定的可靠性分析。

### 4.2 Petrovskaya & Zendle (2022)：玩家视角下的问题商业化

**Reference**  
Petrovskaya, E., & Zendle, D. (2022). Predatory monetisation? A categorisation of unfair, misleading and aggressive monetisation techniques in digital games from the player perspective. *Journal of Business Ethics, 181*, 1065–1081. https://doi.org/10.1007/s10551-021-04970-6

**可借用内容**

- 35 种玩家认为 unfair、misleading 或 aggressive 的机制。
- 八个主要领域：推动消费的游戏动态、产品不符预期、基本体验货币化、掠夺式广告、游戏内货币、P2W、微交易本身和其他。
- 具体机制包括 pay-or-grind、pay-or-wait、nerf cycle、价格掩蔽、固定货币包、诱导广告、限时优惠等。

**本项目边界**

- 调查问题主动要求回忆问题体验，不能据此估计自然 Steam 语料中的 prevalence。
- 玩家 perception 不等于对底层算法、意图或违法性的事实确认。

### 4.3 Petrovskaya, Deterding, & Zendle (2022)：真实评论与公开 codebook

**Reference**  
Petrovskaya, E., Deterding, S., & Zendle, D. (2022). Prevalence and salience of problematic microtransactions in top-selling mobile and PC games: A content analysis of user reviews. *Proceedings of the 2022 CHI Conference on Human Factors in Computing Systems*. https://doi.org/10.1145/3491102.3502056

**开放材料**

- [OSF 复现包](https://osf.io/z7gqe/)
- [初版 codebook 下载](https://osf.io/download/7v5d9/)
- [评论分析终版 codebook 下载](https://osf.io/download/gd53t/)

**可借用内容**

- Directed content analysis 的 category / code definition 写法。
- 初版到终版的修改记录。
- 依据实际分歧重命名、澄清或删除模糊代码。
- 评论数据、游戏资料、分析代码和 codebook 共同公开的复现结构。

**本项目边界**：研究只覆盖 microtransactions 且集中于负面评论；适合借用结构和 monetisation 子类，不能成为完整 `PRESENT/ABSENT` 定义。

### 4.4 Hirota & Kuribayashi (2011)：网络条件与多人游戏公平

**Reference**  
Hirota, R., & Kuribayashi, S. (2011). Evaluation of fairness in multiplayer network games. *2011 IEEE Pacific Rim Conference on Communications, Computers and Signal Processing*. https://doi.org/10.1109/PACRIM.2011.6032859

**可借用内容**

- 不同玩家面对的延迟、丢包或网络质量差异可能引发 perceived unfairness。
- 可为 `access_technical` 子类提供窄范围依据。

**本项目边界**：一般卡顿、崩溃或性能差仍不能自动成为不公平；需要出现差别待遇、竞争劣势或机会不对等。

## 5. Codebook 与 annotation guideline 构建方法

### 5.1 DeCuir-Gunby, Marshall, & McCulloch (2011)

**Reference**  
DeCuir-Gunby, J. T., Marshall, P. L., & McCulloch, A. W. (2011). Developing and using a codebook for the analysis of interview data: An example from a professional development research project. *Field Methods, 23*(2), 136–155. https://doi.org/10.1177/1525822X10388468

**可借用内容**：理论驱动与数据驱动代码结合；代码名、定义、示例；训练标注者；通过 pilot 发展可靠性。

### 5.2 O'Connor & Joffe (2020)

**Reference**  
O'Connor, C., & Joffe, H. (2020). Intercoder reliability in qualitative research: Debates and practical guidelines. *International Journal of Qualitative Methods, 19*, 1–13. https://doi.org/10.1177/1609406919899220

**Open copy**：https://discovery.ucl.ac.uk/id/eprint/10091273/

**可借用内容**

- 预先决定 coding unit、代码深度、重复编码范围、可靠性指标和阈值。
- 独立 pilot、比较分歧、修改 coding frame，再用新样本重新测试。
- 对隐含构念进行标注前需要理论训练。

### 5.3 Röttger et al. (2022)：descriptive 与 prescriptive annotation

**Reference**  
Röttger, P., Vidgen, B., Hovy, D., & Pierrehumbert, J. (2022). Two contrasting data annotation paradigms for subjective NLP tasks. *Proceedings of NAACL-HLT 2022*, 175–190. https://doi.org/10.18653/v1/2022.naacl-main.13

**GitHub**：https://github.com/paul-rottger/annotation-paradigms

**可借用内容**

- `descriptive`：保留不同标注者信念的分布。
- `prescriptive`：按明确、冻结的规则训练一致行为。
- 本项目的 gold evaluation 更接近 prescriptive 路线，但仍应保留原始标签、置信度和分歧原因。
- 在 prescriptive 路线中，pilot 分歧是检查 guidelines 是否含糊或不完整的信号。

### 5.4 Mostafazadeh Davani, Díaz, & Prabhakaran (2022)

**Reference**  
Mostafazadeh Davani, A., Díaz, M., & Prabhakaran, V. (2022). Dealing with disagreements: Looking beyond the majority vote in subjective annotations. *Transactions of the Association for Computational Linguistics, 10*, 92–110. https://doi.org/10.1162/tacl_a_00449

**ACL page**：https://aclanthology.org/2022.tacl-1.6/

**可借用内容**

- 主观任务中的分歧可能反映价值、阈值或解释差异，而非单纯错误。
- 不应只保存多数票结果；应保留原始标签或至少保留 uncertainty / disagreement 信息。

### 5.5 Oortwijn, Ossenkoppele, & Betti (2021)

**Reference**  
Oortwijn, Y., Ossenkoppele, T., & Betti, A. (2021). Interrater disagreement resolution: A systematic procedure to reach consensus in annotation tasks. *Proceedings of the Workshop on Human Evaluation of NLP Systems*, 131–141. https://aclanthology.org/2021.humeval-1.15/

**可借用内容**：系统记录分歧、讨论、规则澄清和 adjudication 的流程。

**本项目边界**：强制共识会隐藏真实分歧，因此 `original_label`、`adjudicated_label` 和 `adjudication_reason` 应分别保存。

### 5.6 MacQueen, McLellan, Kay, & Milstein (1998)：codebook entry 的标准字段模板

**Reference**  
MacQueen, K. M., McLellan, E., Kay, K., & Milstein, B. (1998). Codebook development for team-based qualitative analysis. *Cultural Anthropology Methods (CAM Journal), 10*(2), 31–36. https://doi.org/10.1177/1525822X980100020301

**开放全文**：https://qualquant.org/wp-content/uploads/text/MacQueen%20et%20al%201998.pdf

**可借用内容**

- 每个 code 的六字段结构，是 §10 那份 entry 模板的直接来源：code 名 / 简短定义 / 完整定义 / **何时使用（inclusion）** / **何时不使用（exclusion）** / 示例。
- `exclusion` 字段被规定为**强制项而非补充说明**——这正是本项目「难 ≠ 不公平」「发泄 ≠ 指认不公平」必须落到的位置。
- codebook 作为可迭代产物：先起草、试标、按分歧修订、再冻结。
- DeCuir-Gunby et al. (2011)（§5.1）是这一模板在教育研究中的扩展应用，两者配合使用。

**本项目边界**

- 原始场景是 CDC 的**团队**访谈编码，其可靠性机制依赖多名编码者；本项目 gold 阶段是单人三语标注，无法照搬其团队校准环节（见 §12）。
- 模板只规定字段，不提供构念内容，`fairness` 的实质定义仍须来自 §3、§4。

### 5.7 Hershcovich et al. (2022)：跨文化 NLP 的标注适配

**Reference**  
Hershcovich, D., Frank, S., Lent, H., de Lhoneux, M., Abdou, M., Brandl, S., Bugliarello, E., Cabello Piqueras, L., Chalkidis, I., Cui, R., Fierro, C., Margatina, K., Rust, P., & Søgaard, A. (2022). Challenges and strategies in cross-cultural NLP. *Proceedings of ACL 2022*, 6997–7013. https://doi.org/10.18653/v1/2022.acl-long.482

**arXiv**：https://arxiv.org/abs/2203.10020

**可借用内容**

- 说话者与文本不仅按语言分化，也按**文化**分化；跨语言任务的差异可能来自概念本身在不同语言社群中的边界不同，而不只是表层语言差异。
- 支持本项目的一条核心方法要求：codebook **不能只做字面翻译后直接套用**到中文与日文，须在每种语言上单独 pilot，并记录哪些规则跨语言保持一致、哪些允许语言特定的表达适配。
- 为「跨语言差异是构念差异还是标注差异」这一威胁提供可引用的方法论依据。

**本项目边界**

- 该文是 position/survey 性质，不提供可直接执行的 unfairness 标注规则。
- 本项目的三语标注由同一人完成，其主要威胁是**同一标注者的跨语言漂移**，而非该文讨论的跨文化标注者群体差异；不能用该文替代自身的一致性检验设计。

### 5.8 GoEmotions：通过多轮 pilot 改进 taxonomy

**Reference**  
Demszky, D., Movshovitz-Attias, D., Ko, J., Cowen, A., Nemade, G., & Ravi, S. (2020). GoEmotions: A dataset of fine-grained emotions. *Proceedings of ACL 2020*, 4040–4054. https://aclanthology.org/2020.acl-main.372/

**GitHub data**：https://github.com/google-research/google-research/tree/master/goemotions

**可借用内容**

- 多轮 pilot 后删除稀少、难以区分或低一致性的标签。
- 根据真实数据加入遗漏类别并改进标签名称。
- Taxonomy 的可解释性是可靠性的一部分。

## 6. 公开 codebook、annotation guidelines 与字段结构模板

### 6.1 Moral Foundations Twitter Corpus (MFTC)

**Paper**  
Hoover, J., Portillo-Wightman, G., Yeh, L., et al. (2020). Moral Foundations Twitter Corpus: A collection of 35k tweets annotated for moral sentiment. *Social Psychological and Personality Science, 11*(8), 1057–1071. https://doi.org/10.1177/1948550619876629

**Annotation tool**：https://github.com/limteng-rpi/moral_annotation_tool

**可借用内容**

- `fairness / cheating` 与 `nonmoral` 的分离。
- 先判断是否含相关构念，再选择具体类别的顺序式决策。
- 关键词只是 conceptual anchor，不是自动标签。
- 保守标注并持续记录困难案例。

**不可照搬**：Moral Foundations Theory 的 fairness 范围比本项目更宽，且政治/道德语境和游戏评论不同。

### 6.2 Moral Foundations Reddit Corpus (MFRC)

**Paper and codebook appendix**  
Trager, J., Ziabari, A. S., Mostafazadeh Davani, A., et al. (2022). The Moral Foundations Reddit Corpus. arXiv:2208.05545. https://arxiv.org/abs/2208.05545

**Dataset**：https://huggingface.co/datasets/USC-MOLA-Lab/MFRC

**可借用内容**

- Equality 与 Proportionality 的区分。
- Explicit / implicit moral expression。
- Very confident / somewhat confident / not confident。
- 对缺少语境、讽刺和多种同等合理解释的 uncertainty 处理。

**不可照搬**：主要是英语 Reddit 数据，属于宽泛道德标注，而且论文最初以预印本形式发布。

### 6.3 Contextual Abuse Dataset (CAD)

**Paper**  
Vidgen, B., Nguyen, D., Margetts, H., Rossini, P., & Tromble, R. (2021). Introducing CAD: The Contextual Abuse Dataset. *Proceedings of NAACL-HLT 2021*, 2289–2303. https://doi.org/10.18653/v1/2021.naacl-main.182

**GitHub（含 PDF codebook）**：https://github.com/dongpng/cad_naacl2021

**可借用内容**

- 顶层标签与二级分类分开。
- 每个正例保存 evidence rationale / span。
- 标注 guidelines、codebook 版本、errata、独立标注与 adjudication。
- 区分当前文本证据和上下文证据。

**不可照搬**：其 abuse 类别和 Reddit 对话上下文不适用于独立 Steam review。

### 6.4 Social Bias Frames / SBIC

**Paper**  
Sap, M., Gabriel, S., Qin, L., Jurafsky, D., Smith, N. A., & Choi, Y. (2020). Social Bias Frames: Reasoning about social and power implications of language. *Proceedings of ACL 2020*, 5477–5490. https://doi.org/10.18653/v1/2020.acl-main.486

**公开指南/界面**：https://maartensap.com/social-bias-frames/annotationTask.html  
**Dataset**：https://huggingface.co/datasets/allenai/social_bias_frames

**可借用内容**

- 先判断是否存在目标构念，再标对象、机制和隐含主张。
- 允许 `yes / maybe / no / unintelligible` 等过程性判断。
- 将隐含主张规范化成一句完整解释，而不是只依赖关键词。

**本项目可映射字段**：`normalized_claim = 评论者认为 X 不公平，因为 Y`。

**不可照搬**：身份偏见、冒犯性、说话者意图和美国文化框架均不是本项目的标签目标。

### 6.5 HateXplain

**Paper**  
Mathew, B., Saha, P., Yimam, S. M., Biemann, C., Goyal, P., & Mukherjee, A. (2021). HateXplain: A benchmark dataset for explainable hate speech detection. *Proceedings of AAAI, 35*(17), 14867–14875. https://arxiv.org/abs/2012.10289

**GitHub**：https://github.com/hate-alert/HateXplain

**可借用内容**

- 主标签、对象和 rationale span 分开保存。
- 让标签具有可检查的文本依据。
- 保存多个标注者判断，而不是只保留最终类别。

**不可照搬**：hate / offensive / normal 的定义与游戏公平完全不同。

### 6.6 ISHate

**Paper/repository**：https://github.com/benjaminocampo/ISHate

**可借用内容**

- 仓库中单独提供 `annotation_guidelines.pdf`。
- 将主标签和 explicit / implicit、subtle / non-subtle 等辅助属性分离。
- 公开 agreement 分析和数据字段说明。

**不可照搬**：仇恨言论中的 implicit/subtle 不等同于游戏评论中的隐含 unfairness，只能借字段设计。

### 6.7 Multilingual and Multi-Aspect Hate Speech Analysis

**Paper and GitHub**：https://github.com/HKUST-KnowComp/MLMA_hate_speech

**可借用内容**

- 多语言数据中把主标签、directness、target 和 annotator sentiment 分开。
- 提醒项目不要用一个字段同时混合 unfairness、情绪、对象和语言信息。

**不可照搬**：多语言覆盖不代表其构念或标签适用于游戏评论。

### 6.8 HateCheck：对照式硬负例与 minimal pair

**Paper**  
Röttger, P., Vidgen, B., Nguyen, D., Waseem, Z., Margetts, H., & Pierrehumbert, J. (2021). HateCheck: Functional tests for hate speech detection models. *Proceedings of ACL-IJCNLP 2021*, 41–58. https://doi.org/10.18653/v1/2021.acl-long.4

**GitHub（数据与标注结果）**：https://github.com/paul-rottger/hatecheck-data

**可借用内容**

- 把「反例」从 codebook 里的一句说明升级为**成建制的功能测试**：29 个 functionality，3,728 个案例，其中多个类别专门是 **contrastive non-hate**（例如引用仇恨言论以谴责之、针对物体而非群体的辱骂）。
- 每个非正例案例记录**它所对照的正例 ID**，形成 minimal pair。对应到本项目：`难但公平的 boss 设计` ↔ `难是因为机制被做成付费墙`，两句仅在关键归因上不同。
- 公开每个案例的逐标注者结果，并把标注者一致性未达阈值（5 人中不足 4 人同意 gold）的 173 个案例**排除出测试套件而非强行归类**。
- 案例来源于与 NGO 从业者的访谈，即构念边界由领域知情者而非研究者独自划定。

**本项目边界**

- HateCheck 的案例是**模板生成的合成句**，用于诊断模型而非估计真实分布；本项目的 gold set 必须来自真实 Steam 评论，二者不可混用，合成对照集若构建只能作为独立的诊断集（diagnostic set），不计入 prevalence，也不进入训练。
- hate speech 的构念与 unfairness 无关，可借的只有测试套件的**组织方式**。

### 6.9 已有的 `unfair` 标注语料：构念不同，仅供标签设计参照

**CLAUDETTE**  
Lippi, M., Pałka, P., Contissa, G., Lagioia, F., Micklitz, H.-W., Sartor, G., & Torroni (2019). CLAUDETTE: An automated detector of potentially unfair clauses in online terms of service. *Artificial Intelligence and Law, 27*(2), 117–139. https://doi.org/10.1007/s10506-019-09243-2 ｜ [arXiv](https://arxiv.org/abs/1805.01217)

**GUS-Net**（Generalizations / Unfairness / Stereotypes 的 span 级标注）：https://arxiv.org/abs/2410.08388

**记录这一节的原因**

- 定向检索的结论是：**目前没有以「感知不公平」为标签的游戏评论语料**。以 `unfair` 为标签名的公开语料主要是法律条款（CLAUDETTE，9,414 条 ToS 条款，fair / unfair 二分）与社会偏见（GUS-Net，3,739 句，BIO span 标注，token 级 Krippendorff's α = 0.78）。
- 可借的只有两点：`unfair` 作为**二元条款级标签**的可操作化写法；span 级标注配合 α 报告的做法（与 §6.3 CAD、§6.5 HateXplain 一致）。

**不可照搬**

- CLAUDETTE 标的是**条款在法律上可能不公平**（专家依消费者法判断），本项目标的是**评论者主观感知到不公平**，判断主体、证据基础和真值定义完全不同。
- GUS-Net 的 unfairness 指向受保护群体的表征伤害，与游戏机制公平无关。
- 这三者都不能作为本项目 `PRESENT / ABSENT` 的定义来源，只登记于此以说明为何本项目必须自建 codebook。

## 7. Complaint 与一般负面体验：最重要的 hard-negative 来源

### 7.1 Preotiuc-Pietro et al. (2019)：complaint detection

**Reference**  
Preotiuc-Pietro, D., Gaman, M., & Aletras, N. (2019). Automatically identifying complaints in social media. *Proceedings of ACL 2019*, 5008–5019. https://aclanthology.org/P19-1495/

**GitHub**：https://github.com/danielpreotiuc/complaints-social-media

**可借用内容**

- Complaint 涉及现实与有利期待之间的差距，而不仅是负面词汇。
- 可用于组织“不满意、抱怨、辱骂、负面情绪”与更窄的 unfairness 之间的边界。
- Pilot/calibration 样本应与正式 gold 分开。

**不可照搬**：complaint 比 perceived unfairness 范围更宽；bug、困难、低价值和失望可能是 complaint，但仍不必然属于 unfairness。

### 7.2 Singh et al. (2023)：X-CI explainable complaints

**Reference**  
Singh, A., Jain, R., Jha, P., & Saha, S. (2023). Peeking inside the black box: A commonsense-aware generative framework for explainable complaint detection. *Proceedings of ACL 2023*, 7333–7347. https://doi.org/10.18653/v1/2023.acl-long.404

**可借用内容**

- Complaint label、emotion、polarity、severity 和 rationale 分开标注。
- `rationale` 是解释 complaint / non-complaint 判断的因果文本片段。
- 支持本项目将 `unfair_label`、情绪、强度与 `evidence_span` 分开。

## 8. 数据集说明与可复现性模板

### 8.1 Gebru et al.：Datasheets for Datasets

**Reference**  
Gebru, T., Morgenstern, J., Vecchione, B., et al. (2021). Datasheets for datasets. *Communications of the ACM, 64*(12), 86–92. https://arxiv.org/abs/1803.09010

**可借用内容**：记录数据动机、组成、收集过程、标注过程、建议用途、禁用用途、风险与限制。

### 8.2 Hugging Face Dataset Card guide

**Template**：https://github.com/huggingface/datasets/blob/main/templates/README_guide.md

**可借用内容**

- 明确 annotation process、annotator、guidelines、agreement 和 validation。
- 记录语言、来源、许可、隐私、已知偏差和不适合的用途。

### 8.3 MetaHate 的 DATASHEET 示例

**GitHub**：https://github.com/palomapiot/metahate

**可借用内容**：将 `DATASHEET.md` 与数据、analysis、baseline 和 license 放在同一研究仓库中。

**不可照搬**：MetaHate 的目标是统一 hate speech 数据集，不是 fairness。

## 9. 对本项目 codebook 字段的来源映射

| 建议字段 | 主要参考来源 | 用途 |
|---|---|---|
| `unfair_label` | Colquitt；Xia；Smith/Blodgett；Freeman | 二元主标签：`PRESENT / ABSENT` |
| `inclusion` / `exclusion` | MacQueen et al. (1998) | 每个 code 必填的「何时用 / 何时不用」两栏 |
| `contrast_id` | HateCheck | 硬负例指向其对照正例，构成 minimal pair |
| `evidence_span` | CAD；HateXplain；X-CI | 保存支持判断的原文片段 |
| `normalized_claim` | Social Bias Frames | 用一句话写出被违反的公平规范 |
| `subtype` | Colquitt；Freeman；Petrovskaya 系列 | 用于误差分析，可多选，不替代主标签 |
| `explicitness` | MFRC；ISHate | 区分显式和隐式表达 |
| `confidence` | MFRC | `high / medium / low` |
| `borderline`、`uncertainty_reason` | MFRC；Davani et al. | 不把不确定性压缩成虚假的确定标签 |
| `original_label` | Davani et al.；CAD | 保留独立判断 |
| `adjudicated_label`、`adjudication_reason` | CAD；Oortwijn et al. | 裁决结果与原始标签分离 |
| `codebook_version` | CAD；Petrovskaya OSF | 追踪规则变更并防止 holdout 泄漏 |
| dataset card / limitations | Gebru et al.；Hugging Face guide | 交代来源、用途、风险和泛化边界 |

## 10. 从这些来源得到的共同结构

一个可测试的 codebook entry 至少应包含：

```text
label name
one-sentence operational definition
inclusion criteria
exclusion criteria
clear positive examples
clear negative examples
borderline / hard-negative examples
contrastive minimal pairs (hard negative -> the positive it contrasts)
tie-breaker rules
evidence requirements
uncertainty triggers
subtype relationship
version history
```

对本项目而言，建议每条 gold annotation 至少保留：

```text
review_id
language
unfair_label: PRESENT | ABSENT
evidence_span
normalized_claim
subtype: list
explicitness: explicit | implicit
confidence: high | medium | low
borderline: true | false
uncertainty_reason
out_of_scope: true | false
annotator_note
original_label
adjudicated_label
adjudication_reason
codebook_version
```

## 11. 不应从参考资料中直接推出的结论

- 不能因为出现 `unfair`、`rigged`、`scam`、`不公平`、`坑人`、`理不尽` 等词就自动判为 `PRESENT`。
- 不能因为评论是负评、带有愤怒、辱骂或低评分就判为不公平。
- 不能把困难、失败、bug、服务器问题、高价或低价值自动标成不公平。
- 不能把评论者的 perception 写成游戏公司真实意图、客观违法或算法事实。
- 不能把英语语料中的表达规则未经 pilot 直接投射到中文和日文（依据见 §5.7 Hershcovich et al.）。
- 不能用开发阶段的 codebook 修改去追逐正式 holdout 分数；正式评估前必须冻结版本。
- 不能只保留 adjudicated label 而删除原始标签、置信度和裁决理由。

## 12. 检索与证据限制

- 这是围绕 codebook 起草开展的快速定向检索，不是 PRISMA 系统综述。
- 优先保留同行评审论文、DOI、作者公开版本、ACL Anthology、正式 GitHub 仓库、OSF 和机构数据页面。
- GitHub 仓库用于验证实际 guidelines、字段和公开材料，不能因 star 数或代码可运行而提升构念证据等级。
- 游戏领域最直接的来源主要集中于英文、Reddit、竞技游戏和 monetisation；它们对中文、日文 Steam 评论及单人游戏的适用性仍需通过本项目 pilot 验证。
- 本文档使用 AI 辅助检索与整理；链接、DOI、正式仓库和主要方法信息已对照论文、出版社或机构页面核验。

### 12.1 尚未闭合的两个缺口（2026-08-05 补记）

1. **Freeman et al. (2022) 的完整编码表尚未取得。** 作者站 PDF 为图片型无法抽取文本，ACM 页面返回 403。§4.1「可借用内容」目前依据的是摘要与二手综述，**不是其编码表原文**。取得机构权限版本前，不得声称本项目维度已获该研究实证支持。
2. **单人三语标注的一致性方法缺少对应文献。** §5 收集的可靠性方法（O'Connor & Joffe、Davani、Oortwijn、MacQueen）全部预设**多名标注者**。本项目 gold 阶段为一人标注 EN/ZH/JA，主要效度威胁是**同一标注者在三种语言间的判准漂移**——若发生，将无法与「模型在某语言上更差」这一目标结论区分开。当前尚未找到直接可引用的处理方案，暂定自行设计 intra-rater（test–retest）检验并在此处补记来源。此缺口在 codebook 冻结前必须有明确处置。
