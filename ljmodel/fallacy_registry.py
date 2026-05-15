"""统一谬误分类注册表 — 覆盖9本书框架的完整逻辑谬误体系

本文件是系统的"谬误字典"，包含：
1. 每种谬误的中英文名称、分类、来源书籍、详细说明
2. 规则引擎可用的关键词匹配列表
3. 供LLM提示词引用的完整分类描述

使用方式：
  - FALLACY_REGISTRY: 包含所有谬误的完整列表
  - get_fallacies_by_category(cat): 按分类筛选
  - get_fallacies_by_book(book): 按来源书筛选
  - match_keyword_fallacies(text): 用关键词匹配检测
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Fallacy:
    """谬误条目"""
    id: str                          # 唯一标识符
    chinese_name: str                # 中文名
    english_name: str                # 英文名
    category: str                    # 分类（形式/歧义/关联/假设/归纳/偏见/论证/非逻辑/结构/辩证/源思维）
    subcategory: str                 # 子分类
    source_book: str                 # 来源书籍
    description: str                 # 详细说明
    detection_hint: str = ""         # 检测提示（供LLM使用）
    keywords: list[str] = field(default_factory=list)   # 关键词匹配（供规则引擎使用）
    severity: str = "中"             # 典型严重程度


# ========================================================================
# 第一部分：形式谬误 — Formal Fallacies
# 推理形式本身无效，与内容无关
# 来源：《逻辑学十五讲》《简单的逻辑学》
# ========================================================================

FORMAL_FALLACIES = [
    Fallacy(
        id="deny_antecedent",
        chinese_name="否定前件",
        english_name="Denying the Antecedent",
        category="形式谬误", subcategory="假言推理谬误",
        source_book="逻辑学十五讲",
        description="如果P则Q，但非P，所以非Q。这是无效推理：P只是Q的充分条件，非P不意味着非Q。",
        detection_hint="检查 '如果...那么...' 结构：前提否定了条件句的前件，就推出否定后件",
        keywords=["如果", "那么", "不", "没有", "并非"],
        severity="高"
    ),
    Fallacy(
        id="affirm_consequent",
        chinese_name="肯定后件",
        english_name="Affirming the Consequent",
        category="形式谬误", subcategory="假言推理谬误",
        source_book="逻辑学十五讲",
        description="如果P则Q，Q，所以P。这是无效推理：Q可能有其他原因，不能由Q推出P。",
        detection_hint="检查 '如果...那么...' 结构：结论肯定了条件句的后件，就推出前件",
        keywords=["如果", "那么", "是", "因为"],
        severity="高"
    ),
    Fallacy(
        id="four_terms",
        chinese_name="四项谬误",
        english_name="Four-Term Fallacy (Quaternio Terminorum)",
        category="形式谬误", subcategory="三段论谬误",
        source_book="逻辑学十五讲",
        description="三段论需要三个项（中项、大项、小项），如果出现四个不同的项，三段论必然无效。常因偷换概念导致。",
        detection_hint="检查三段论是否暗中引入了第四个概念，导致中项失去桥梁作用",
        keywords=[],
        severity="高"
    ),
    Fallacy(
        id="undistributed_middle",
        chinese_name="中项不周延",
        english_name="Undistributed Middle",
        category="形式谬误", subcategory="三段论谬误",
        source_book="逻辑学十五讲",
        description="三段论的中项必须至少周延一次（即对全类有所断定）。如果中项在两个前提中都不周延，则前提和结论之间的逻辑桥梁断裂。",
        detection_hint="检查中项是否在两个前提中都被部分地使用（如'有些X是Y，有些Y是Z'）",
        keywords=["有些", "有的", "部分"],
        severity="高"
    ),
    Fallacy(
        id="illicit_major",
        chinese_name="大项不当周延",
        english_name="Illicit Major",
        category="形式谬误", subcategory="三段论谬误",
        source_book="逻辑学十五讲",
        description="结论中大项周延（对全类做断定），但在前提中大项不周延，导致结论超出了前提所能支持的范围。",
        detection_hint="检查结论中关于大项的全称断定是否超出了前提中给出的信息",
        keywords=[],
        severity="高"
    ),
    Fallacy(
        id="illicit_minor",
        chinese_name="小项不当周延",
        english_name="Illicit Minor",
        category="形式谬误", subcategory="三段论谬误",
        source_book="逻辑学十五讲",
        description="结论中小项周延，但在前提中小项不周延。与小项在结论中的范围超出前提中的范围。",
        detection_hint="检查结论中的全称断定是否超出了前提的范围",
        keywords=[],
        severity="高"
    ),
    Fallacy(
        id="exclusive_premises",
        chinese_name="双否定前提",
        english_name="Exclusive Premises",
        category="形式谬误", subcategory="三段论谬误",
        source_book="逻辑学十五讲",
        description="两个前提都是否定命题时，无法推出任何确定结论。否定前提切断而非建立了项之间的关系。",
        detection_hint="检查是否两个前提都是否定形式（'不是''没有'）",
        keywords=["不是", "没有", "并非"],
        severity="中"
    ),
    Fallacy(
        id="affirm_negative",
        chinese_name="肯定前提推否定结论",
        english_name="Affirmative from a Negative",
        category="形式谬误", subcategory="三段论谬误",
        source_book="逻辑学十五讲",
        description="前提都是肯定命题，但结论是否定命题。肯定前提不能推出否定结论。",
        detection_hint="检查前提均为肯定形式，但结论却是否定形式",
        keywords=[],
        severity="中"
    ),
    Fallacy(
        id="existential_fallacy",
        chinese_name="存在性预设谬误",
        english_name="Existential Fallacy",
        category="形式谬误", subcategory="三段论谬误",
        source_book="逻辑学十五讲",
        description="从全称前提推出特称结论时错误地预设了主项的存在。例如'所有鬼魂都是可怕的，所以有些鬼魂是可怕的'——鬼魂不存在。",
        detection_hint="检查从全称到特称的推理是否预设了类别成员的存在",
        keywords=["所有", "每个", "有些", "存在"],
        severity="中"
    ),
    Fallacy(
        id="modal_fallacy",
        chinese_name="模态谬误",
        english_name="Modal Fallacy",
        category="形式谬误", subcategory="模态推理谬误",
        source_book="逻辑学十五讲",
        description="混淆了必然性和可能性的推理。例如从'可能P'推出'必然P'，或从'必然非P'推出'不可能P'的混淆。",
        detection_hint="检查关于必然/可能/不可能等模态词的推理是否合理",
        keywords=["必然", "可能", "不可能", "一定", "或许"],
        severity="高"
    ),
    Fallacy(
        id="quantifier_shift",
        chinese_name="量词转换谬误",
        english_name="Quantifier Shift Fallacy",
        category="形式谬误", subcategory="量化推理谬误",
        source_book="逻辑学十五讲",
        description="错误地交换了不同量词的顺序。'每个人都有一个母亲'≠'有一个人是所有人之母'。",
        detection_hint="检查 '所有...存在...' 和 '存在...所有...' 是否被混淆",
        keywords=["所有", "每一个", "存在", "有"],
        severity="中"
    ),
    Fallacy(
        id="false_conversion",
        chinese_name="换位错误",
        english_name="False Conversion",
        category="形式谬误", subcategory="词项逻辑谬误",
        source_book="逻辑学十五讲",
        description="错误地将命题的主项和谓项互换。'所有A是B'不能推出'所有B是A'。只有E命题和I命题可以简单换位。",
        detection_hint="检查是否从 '所有A都是B' 错误地推出 '所有B都是A'",
        keywords=["所有", "都是", "全是"],
        severity="中"
    ),
]

# ========================================================================
# 第二部分：歧义性谬误 — Fallacies of Ambiguity
# 因语言歧义导致的推理错误
# 来源：《逻辑学十五讲》《学会提问》
# ========================================================================

AMBIGUITY_FALLACIES = [
    Fallacy(
        id="equivocation",
        chinese_name="偷换概念",
        english_name="Equivocation",
        category="歧义性谬误", subcategory="词义歧义",
        source_book="逻辑学十五讲",
        description="在同一论证中关键术语的含义发生改变。同一个词在前提中是一个意思，在结论中变成另一个意思。",
        detection_hint="检查关键术语在论证前后是否保持了同一含义，尤其是抽象/多义词（如'自由''权利''自然''本质'）",
        keywords=["偷换概念", "混淆概念", "概念混淆", "偷换"],
        severity="高"
    ),
    Fallacy(
        id="amphiboly",
        chinese_name="歧义句/浑水摸鱼",
        english_name="Amphiboly",
        category="歧义性谬误", subcategory="句法歧义",
        source_book="逻辑学十五讲",
        description="由于句子语法结构歧义导致误解。同一个句子可能有两种或多种合理解读。",
        detection_hint="检查是否有句子可以作多种语法结构解读，而论证利用了这种歧义",
        keywords=["歧义", "可以理解为", "既可以"],
        severity="中"
    ),
    Fallacy(
        id="accent",
        chinese_name="错置重音",
        english_name="Accent (Fallacy of Emphasis)",
        category="歧义性谬误", subcategory="语用歧义",
        source_book="逻辑学十五讲",
        description="通过改变重音、强调或语调来改变句子的含义。引用时断章取义也属此类。",
        detection_hint="检查是否通过强调不同词语或断章取义来歪曲原意",
        keywords=["断章取义", "引用的部分", "强调"],
        severity="中"
    ),
    Fallacy(
        id="composition",
        chinese_name="合举谬误/合成谬误",
        english_name="Fallacy of Composition",
        category="歧义性谬误", subcategory="部分-整体谬误",
        source_book="逻辑学十五讲",
        description="错误地认为整体的每一部分有某属性，则整体也有该属性。部分具备的属性不必然传递给整体。",
        detection_hint="检查是否从部分的属性推到了整体的属性（如'每个部件都很轻，所以整台机器很轻'）",
        keywords=["合举", "合成谬误", "整体", "每个部分", "各个"],
        severity="中"
    ),
    Fallacy(
        id="division",
        chinese_name="分举谬误/分解谬误",
        english_name="Fallacy of Division",
        category="歧义性谬误", subcategory="部分-整体谬误",
        source_book="逻辑学十五讲",
        description="错误地认为整体有某属性，则每一部分也有该属性。整体的属性不必然属于其每个部分。",
        detection_hint="检查是否从整体的属性推到了部分的属性（如'这台机器是精密的，所以每个零件都是精密的'）",
        keywords=["分举", "分解谬误", "整体", "每个"],
        severity="中"
    ),
    Fallacy(
        id="reification",
        chinese_name="具体化谬误/实体化谬误",
        english_name="Reification (Hypostatization)",
        category="歧义性谬误", subcategory="抽象-具体混淆",
        source_book="逻辑学十五讲",
        description="把抽象概念当作具体实体来对待。将不是真实事物的抽象名词当作真实存在的事物。",
        detection_hint="检查是否把抽象概念（如'正义''社会''命运'）当成了能行动的具体事物",
        keywords=["命运", "社会", "自然", "历史", "正义", "必将", "不会让"],
        severity="低"
    ),
    Fallacy(
        id="defined_term",
        chinese_name="关键概念未定义",
        english_name="Key Term Not Defined",
        category="歧义性谬误", subcategory="定义模糊",
        source_book="学会提问",
        description="论证使用了关键抽象概念但没有给出清晰定义。对方可能在不同含义上理解该词。",
        detection_hint="检查是否有反复出现但对论证至关重要的抽象词未做定义",
        keywords=["自由", "公平", "正义", "民主", "人权", "本质", "科学"],
        severity="中"
    ),
    Fallacy(
        id="weasel_words",
        chinese_name="闪避式语言",
        english_name="Weasel Words / Evasive Language",
        category="歧义性谬误", subcategory="语言模糊",
        source_book="简单的逻辑学",
        description="使用模糊、不确定的语言来回避真实表达立场。用空洞的修饰语避免承担论证责任。",
        detection_hint="检查是否有大量模糊限定词（'可能''大概''也许''某种意义上'等）",
        keywords=["某种意义上", "可以说", "基本上", "所谓的"],
        severity="低"
    ),
]

# ========================================================================
# 第三部分：关联性谬误 — Fallacies of Relevance
# 前提与结论在逻辑上无关，但用心理/情感联系代替
# 来源：《逻辑学十五讲》《学会提问》《批判性思维工具》
# ========================================================================

RELEVANCE_FALLACIES = [
    Fallacy(
        id="ad_hominem",
        chinese_name="人身攻击",
        english_name="Ad Hominem (Argument Against the Person)",
        category="关联性谬误", subcategory="人身相关",
        source_book="逻辑学十五讲",
        description="攻击提出论证的人而非论证本身。包括人身攻击型、处境型、你也一样型（tu quoque）。",
        detection_hint="检查是否针对发言人的人格/动机/行为而非论证本身进行攻击",
        keywords=["人身攻击", "你这个人", "你自己也", "你有什么资格"],
        severity="高"
    ),
    Fallacy(
        id="ad_populum",
        chinese_name="诉诸公众/诉诸群众",
        english_name="Ad Populum (Appeal to the People)",
        category="关联性谬误", subcategory="情感关联",
        source_book="逻辑学十五讲",
        description="以多数人的意见或流行程度作为真理标准。'大家都相信'不等于'这是真的'。",
        detection_hint="检查是否以'大众认同''流行''多数'作为论证依据",
        keywords=["诉诸公众", "诉诸群众", "大家都", "人人都", "每个人都知道", "公认"],
        severity="中"
    ),
    Fallacy(
        id="ad_misericordiam",
        chinese_name="诉诸怜悯",
        english_name="Appeal to Pity (Ad Misericordiam)",
        category="关联性谬误", subcategory="情感关联",
        source_book="逻辑学十五讲",
        description="用同情、怜悯等情感代替逻辑论证。激发听众的同情心而非提供理性理由。",
        detection_hint="检查是否用可怜/值得同情的描述代替了事实论据",
        keywords=["诉诸怜悯", "太可怜了", "好可怜", "令人同情"],
        severity="中"
    ),
    Fallacy(
        id="ad_verecundiam",
        chinese_name="诉诸权威",
        english_name="Appeal to Authority (Ad Verecundiam)",
        category="关联性谬误", subcategory="情感关联",
        source_book="逻辑学十五讲",
        description="引用权威在非自身专业领域的判断作为证据。名人代言科学产品、经济学家谈医学等。",
        detection_hint="检查引用的权威是否在其专业领域内，以及该领域是否有共识",
        keywords=["诉诸权威", "专家说", "研究表明", "科学家认为"],
        severity="中"
    ),
    Fallacy(
        id="ad_ignorantiam",
        chinese_name="诉诸无知",
        english_name="Appeal to Ignorance (Ad Ignorantiam)",
        category="关联性谬误", subcategory="情感关联",
        source_book="逻辑学十五讲",
        description="因为无法证明某事为假，所以为真（或反之）。缺乏证据不等于证据。",
        detection_hint="检查是否以'不能证明不存在所以存在'或'不能证明存在所以不存在'的方式论证",
        keywords=["诉诸无知", "无法证明", "不能证伪", "没有证据表明", "不能否定"],
        severity="中"
    ),
    Fallacy(
        id="ad_baculum",
        chinese_name="诉诸强力/诉诸恐惧",
        english_name="Appeal to Force (Ad Baculum) / Appeal to Fear",
        category="关联性谬误", subcategory="情感关联",
        source_book="逻辑学十五讲",
        description="用威胁、恐吓或暗示负面后果来使人接受结论，而非提供理性论证。",
        detection_hint="检查是否用威胁性语言或制造恐惧来替代理性论证",
        keywords=["诉诸强力", "诉诸恐惧", "否则", "后果", "危险", "威胁", "可怕"],
        severity="高"
    ),
    Fallacy(
        id="ad_hominem_circumstantial",
        chinese_name="处境人身攻击",
        english_name="Circumstantial Ad Hominem",
        category="关联性谬误", subcategory="人身相关",
        source_book="逻辑学十五讲",
        description="因为发言人处境/利益/背景而否定其论证。'他只是为了利益才这么说'。",
        detection_hint="检查是否以说话人的处境、利益或立场来否定其论证的合理性",
        keywords=["他只是为了", "当然会这么说", "因为他有利益", "位置决定"],
        severity="中"
    ),
    Fallacy(
        id="tu_quoque",
        chinese_name="你也一样/两错谬误",
        english_name="Tu Quoque (You Too)",
        category="关联性谬误", subcategory="人身相关",
        source_book="逻辑学十五讲",
        description="通过指责对方也做了同样的事来回避批评。'你凭什么批评我？你自己也这样！'。",
        detection_hint="检查是否用'你也不例外''你也一样'来回应对论证的批评",
        keywords=["你也一样", "你自己也", "你凭什么", "你也有"],
        severity="中"
    ),
    Fallacy(
        id="straw_man",
        chinese_name="稻草人谬误",
        english_name="Straw Man Fallacy",
        category="关联性谬误", subcategory="歪曲论证",
        source_book="逻辑学十五讲",
        description="歪曲、简化或夸大对方的论点，然后攻击这个被歪曲后的版本，而非真正的主张。",
        detection_hint="检查是否把一个更容易反驳的立场强加给对方，然后攻击它",
        keywords=["稻草人", "曲解", "夸大", "你们的意思不就是"],
        severity="高"
    ),
    Fallacy(
        id="red_herring",
        chinese_name="红鲱鱼/转移注意",
        english_name="Red Herring",
        category="关联性谬误", subcategory="歪曲论证",
        source_book="逻辑学十五讲",
        description="引入一个与当前论证无关的话题来转移注意力，逃避对原问题的讨论。",
        detection_hint="检查是否引入了与当前话题无关的新议题来转移焦点",
        keywords=["先不说", "重要的是", "真正的问题", "难道不是"],
        severity="中"
    ),
    Fallacy(
        id="ad_hoc",
        chinese_name="特设性辩护",
        english_name="Ad Hoc Rescue / Special Pleading",
        category="关联性谬误", subcategory="偏颇论证",
        source_book="批判性思维工具",
        description="为挽救一个已被反驳的立场，临时添加一个特殊的例外理由，而不修改原立场。",
        detection_hint="检查是否在遇到反例时引入特殊的、无法被检验的例外条件",
        keywords=["但情况不同", "有例外", "因为特殊原因", "不适用于"],
        severity="中"
    ),
    Fallacy(
        id="no_true_scotsman",
        chinese_name="没有真正的苏格兰人",
        english_name="No True Scotsman",
        category="关联性谬误", subcategory="偏颇论证",
        source_book="批判性思维工具",
        description="遇到反例时通过重新定义类别来排除反例，而不修正原来的概括。'所有X都是Y'→'但某个X不是Y'→'那他就不是真正的X'。",
        detection_hint="检查是否在遇到反例时通过收紧定义来排除反例，而非修改原命题",
        keywords=["真正的", "不是真正的", "本质上", "根本不是"],
        severity="中"
    ),
    Fallacy(
        id="appeal_to_nature",
        chinese_name="诉诸自然",
        english_name="Appeal to Nature",
        category="关联性谬误", subcategory="情感关联",
        source_book="学会提问",
        description="因为某事物是'自然的'就认为它是好的/正确的，或因为某事物是'不自然的'就认为它是坏的。自然≠好。",
        detection_hint="检查是否以'天然''自然''纯天然'作为正确性的理由",
        keywords=["天然", "纯天然", "自然的就是好的", "不自然"],
        severity="低"
    ),
    Fallacy(
        id="appeal_to_novelty",
        chinese_name="诉诸新颖",
        english_name="Appeal to Novelty",
        category="关联性谬误", subcategory="情感关联",
        source_book="学会提问",
        description="因为某事物是新的/现代的/革新的就认为它更好。新颖≠正确。",
        detection_hint="检查是否以'新''最新''革新''突破'作为正确性的理由",
        keywords=["最新", "革新", "突破性", "划时代"],
        severity="低"
    ),
    Fallacy(
        id="appeal_to_tradition",
        chinese_name="诉诸传统",
        english_name="Appeal to Tradition",
        category="关联性谬误", subcategory="情感关联",
        source_book="学会提问",
        description="因为某事物是传统的/一直如此的/历来如此的就认为它正确。传统≠正确。",
        detection_hint="检查是否以'历来如此''传统上''老祖宗'作为正确性的理由",
        keywords=["传统", "历来", "老祖宗", "一直以来都", "从来如此"],
        severity="低"
    ),
    Fallacy(
        id="appeal_to_wealth",
        chinese_name="诉诸财富",
        english_name="Appeal to Wealth",
        category="关联性谬误", subcategory="情感关联",
        source_book="学会提问",
        description="因为某事物是富人的选择/昂贵的/成功的标志就认为它正确。经济上的成功不等于论证的正确。",
        detection_hint="检查是否以'富人''成功人士''有钱'作为正确性的理由",
        keywords=["富人", "成功人士", "有钱人都"],
        severity="低"
    ),
    Fallacy(
        id="appeal_to_ridicule",
        chinese_name="诉诸嘲笑/以笑饰非",
        english_name="Appeal to Ridicule (Reductio ad Ridiculum)",
        category="关联性谬误", subcategory="情感关联",
        source_book="简单的逻辑学",
        description="通过嘲笑、讽刺或漫画化对方观点来回避实质论证。幽默不等于反驳。",
        detection_hint="检查是否用嘲笑、讽刺、夸张来取代实质性的反驳",
        keywords=["以笑饰非", "太可笑了", "真荒谬", "荒唐"],
        severity="低"
    ),
    Fallacy(
        id="appeal_to_hypocrisy",
        chinese_name="诉诸虚伪",
        english_name="Appeal to Hypocrisy",
        category="关联性谬误", subcategory="人身相关",
        source_book="逻辑学十五讲",
        description="指出对方行为与其主张不一致，就认为对方的主张是错的。言行不一≠主张错误。",
        detection_hint="检查是否用指出对方虚伪来替代反驳对方的论证",
        keywords=["言行不一", "你嘴上说", "自己都做不到"],
        severity="中"
    ),
    Fallacy(
        id="genetic_fallacy",
        chinese_name="起源谬误/以出身论英雄",
        english_name="Genetic Fallacy",
        category="关联性谬误", subcategory="人身相关",
        source_book="简单的逻辑学",
        description="因某主张的来源/出身/历史而肯定或否定它，而非基于其本身的论证。",
        detection_hint="检查是否因为来源（人/机构/时代）而接受或拒绝一个主张，而非其论证本身",
        keywords=["以出身论英雄", "来源于", "来自", "出身"],
        severity="中"
    ),
    Fallacy(
        id="middle_ground",
        chinese_name="中庸谬误/折中谬误",
        english_name="Middle Ground Fallacy (Argument to Moderation)",
        category="关联性谬误", subcategory="歪曲论证",
        source_book="学会提问",
        description="因为两个极端立场之间的中间立场看起来更合理，就认为中间立场是正确的。折中≠真理。",
        detection_hint="检查是否默认'折中方案'一定最优，而没有分别考察两个极端的论据",
        keywords=["折中", "中庸", "中间路线", "平衡"],
        severity="中"
    ),
]

# ========================================================================
# 第四部分：假设性谬误 — Fallacies of Presumption
# 推理建立在未经验证的隐含假设之上
# 来源：《逻辑学十五讲》《简单的逻辑学》《学会提问》
# ========================================================================

PRESUMPTION_FALLACIES = [
    Fallacy(
        id="begging_question",
        chinese_name="循环论证/乞题",
        english_name="Begging the Question (Circular Reasoning)",
        category="假设性谬误", subcategory="窃取论题",
        source_book="逻辑学十五讲",
        description="论证的前提中已经包含了待证明的结论。论证在原地打转，没有提供新的理据。",
        detection_hint="检查结论是否被（可能以不同措辞）直接用作前提",
        keywords=["循环论证", "因为", "所以", "本来就是"],
        severity="高"
    ),
    Fallacy(
        id="false_dilemma",
        chinese_name="非黑即白/虚假两难",
        english_name="False Dilemma / False Dichotomy",
        category="假设性谬误", subcategory="虚假限定",
        source_book="逻辑学十五讲",
        description="只提供两种极端选择并强迫对方选择其一，忽略中间地带的多种可能性。",
        detection_hint="检查论证框架是否只给出了两种可能性，且被表述为'要么...要么...'",
        keywords=["非黑即白", "要么", "要么就", "不是", "就是", "别无选择"],
        severity="高"
    ),
    Fallacy(
        id="slippery_slope",
        chinese_name="滑坡谬误",
        english_name="Slippery Slope",
        category="假设性谬误", subcategory="虚假限定",
        source_book="逻辑学十五讲",
        description="声称允许A发生就必然导致Z（通常是极端负面结果），但没有提供中间步骤的因果证据。",
        detection_hint="检查是否预言一系列连锁反应但未证明每个环节的因果关系",
        keywords=["滑坡谬误", "一旦", "就会", "最终", "总有一天"],
        severity="中"
    ),
    Fallacy(
        id="hasty_generalization",
        chinese_name="以偏概全/轻率概括",
        english_name="Hasty Generalization (Secundum Quid)",
        category="假设性谬误", subcategory="不当归纳",
        source_book="逻辑学十五讲",
        description="样本数量不足或不具代表性就做出一般性结论。个别案例不足以支持普遍命题。",
        detection_hint="检查是否从有限的案例推出了一个全称结论",
        keywords=["以偏概全", "都", "总是", "永远", "所有", "从没见过"],
        severity="高"
    ),
    Fallacy(
        id="false_cause",
        chinese_name="虚假原因",
        english_name="False Cause (Non Causa Pro Causa)",
        category="假设性谬误", subcategory="因果谬误",
        source_book="逻辑学十五讲",
        description="将两件事的相关性误认为因果关系。A和B同时发生/先后发生不等于A导致B。",
        detection_hint="检查是否把相关性、时间先后或伴随关系直接等同于因果关系",
        keywords=["虚假原因", "导致", "引起", "因为", "所以", "于是"],
        severity="高"
    ),
    Fallacy(
        id="post_hoc",
        chinese_name="以先后为因果",
        english_name="Post Hoc Ergo Propter Hoc",
        category="假设性谬误", subcategory="因果谬误",
        source_book="逻辑学十五讲",
        description="因为事件A在事件B之前发生，所以A是B的原因。时间先后不等于因果关系。",
        detection_hint="检查是否因为一件事发生在另一件事之前就认为是原因",
        keywords=["以先后为因果", "之后", "然后", "接着", "从此"],
        severity="中"
    ),
    Fallacy(
        id="slippery_slope_weak",
        chinese_name="弱滑坡谬误",
        english_name="Weak Analogy Slippery Slope",
        category="假设性谬误", subcategory="不当类比",
        source_book="逻辑学十五讲",
        description="使用极端但缺乏实质相似性的类比来论证。将当前情况与极端但不可比的情况强行类比。",
        detection_hint="检查类比是否在关键属性上缺乏实质相似性",
        keywords=["这不就相当于", "好比", "如同", "相当于"],
        severity="中"
    ),
    Fallacy(
        id="complex_question",
        chinese_name="复杂问语",
        english_name="Complex Question (Plurium Interrogationum)",
        category="假设性谬误", subcategory="预设谬误",
        source_book="逻辑学十五讲",
        description="提问中包含了未经证实的预设。无论回答'是'还是'否'，都承认了该预设。",
        detection_hint="检查问题中是否隐藏了一个作为预设的未证命题",
        keywords=["复杂问语", "你还在", "你什么时候", "你是不是已经"],
        severity="中"
    ),
    Fallacy(
        id="question_begging_epithet",
        chinese_name="乞题修饰语",
        english_name="Question-Begging Epithet",
        category="假设性谬误", subcategory="窃取论题",
        source_book="逻辑学十五讲",
        description="用含价值判断的修饰语代替论证，如'这种野蛮的做法'、'这个明智的决定'。修饰语隐含了待证明的结论。",
        detection_hint="检查是否使用了带有强烈价值判断的修饰语来代替理性论证",
        keywords=["野蛮", "明智", "愚蠢", "荒谬", "合理的"],
        severity="低"
    ),
    Fallacy(
        id="loaded_question",
        chinese_name="诱导性提问",
        english_name="Loaded Question",
        category="假设性谬误", subcategory="预设谬误",
        source_book="学会提问",
        description="问题本身包含了误导性预设或情感负载，诱导回答者落入陷阱。",
        detection_hint="检查问题是否通过预设来限制或诱导回答方向",
        keywords=["难道不", "你不觉得", "是不是应该", "难道你"],
        severity="中"
    ),
    Fallacy(
        id="gambler_fallacy",
        chinese_name="赌徒谬误",
        english_name="Gambler's Fallacy",
        category="假设性谬误", subcategory="概率谬误",
        source_book="逻辑学十五讲",
        description="错误地认为独立随机事件的概率受历史结果影响。硬币连续5次正面后，第6次正面的概率仍然是50%。",
        detection_hint="检查是否把独立事件的概率当作受历史影响的相关事件",
        keywords=["赌徒谬误", "连续几次", "该轮到", "不可能再", "运气该转了"],
        severity="低"
    ),
    Fallacy(
        id="base_rate",
        chinese_name="基率谬误",
        english_name="Base Rate Fallacy / Base Rate Neglect",
        category="假设性谬误", subcategory="概率谬误",
        source_book="思考快与慢",
        description="做判断时忽略基础概率，过分关注具体个案的信息。在低基础概率的情况下，即使检测准确率很高，阳性结果也大概率是误报。",
        detection_hint="检查是否忽略了事件在总体中的基础发生概率，只关注个案特征",
        keywords=["概率", "比例", "百分之", "可能性"],
        severity="中"
    ),
    Fallacy(
        id="conjunction_fallacy",
        chinese_name="合取谬误",
        english_name="Conjunction Fallacy",
        category="假设性谬误", subcategory="概率谬误",
        source_book="思考快与慢",
        description="认为两个事件的合取概率大于其中单个事件的概率。'Linda是女权主义者+银行柜员'的概率不可能大于'Linda是银行柜员'的概率。",
        detection_hint="检查是否认为具体详细的情景比一般概括更可能发生",
        keywords=["又是", "同时是", "并且是"],
        severity="中"
    ),
    Fallacy(
        id="expectation_fulfilled",
        chinese_name="预期理由",
        english_name="Expectation Fulfilled / Wishful Thinking",
        category="假设性谬误", subcategory="预设谬误",
        source_book="逻辑学十五讲",
        description="用尚未被证实的命题作为论据。前提本身还没有被证实，就把它当作确定的事实来推出结论。",
        detection_hint="检查关键前提是否本身就是一个需要被证实的假设",
        keywords=["预期理由", "如果", "假设", "假定", "设想"],
        severity="中"
    ),
    Fallacy(
        id="suppressed_evidence",
        chinese_name="隐藏证据/省略信息",
        english_name="Suppressed Evidence / Cherry Picking",
        category="假设性谬误", subcategory="证据谬误",
        source_book="学会提问",
        description="只选择支持自己立场的证据，而忽略或隐藏反面证据。选择性呈现实质上扭曲了论证的完整性。",
        detection_hint="检查是否只呈现了支持性证据，而明显缺少反面或矛盾信息",
        keywords=["省略了", "没有提到", "另一方", "反面的"],
        severity="高"
    ),
    Fallacy(
        id="false_analogy",
        chinese_name="不当类比",
        english_name="False Analogy / Weak Analogy",
        category="假设性谬误", subcategory="不当类比",
        source_book="论证是一门学问",
        description="在两个事物之间进行类比，但它们在关键属性上缺乏实质相似性，导致类比论证无效。",
        detection_hint="检查类比涉及的两个事物在论证所依赖的关键属性上是否真正可比",
        keywords=["好比", "就像是", "如同", "类比", "相当于"],
        severity="中"
    ),
    Fallacy(
        id="over_simplification",
        chinese_name="过度简化",
        english_name="Over-Simplification / Oversimplified Cause",
        category="假设性谬误", subcategory="因果谬误",
        source_book="论证是一门学问",
        description="将复杂结果归因于单一原因，忽略了多因素交织的实际情况。",
        detection_hint="检查是否将复杂问题归因于一个简单原因，忽略了其他可能因素",
        keywords=["唯一原因", "主要因素", "归根结底", "说白了", "无非是"],
        severity="中"
    ),
    Fallacy(
        id="single_cause",
        chinese_name="单一原因谬误",
        english_name="Single Cause Fallacy (Causal Oversimplification)",
        category="假设性谬误", subcategory="因果谬误",
        source_book="论证是一门学问",
        description="假定只有一个原因导致了某个结果，而实际上可能存在多个共同作用的原因。",
        detection_hint="检查是否将结果归因于单一因素，排除其他可能的原因",
        keywords=["只是", "原因就在于", "唯一的原因是"],
        severity="中"
    ),
]

# ========================================================================
# 第五部分：认知偏见 — Cognitive Biases (Kahneman)
# 系统1快思维导致的系统性认知偏差
# 来源：《思考,快与慢》
# ========================================================================

COGNITIVE_BIASES = [
    Fallacy(
        id="confirmation_bias",
        chinese_name="确认偏误",
        english_name="Confirmation Bias",
        category="认知偏见", subcategory="信息处理",
        source_book="思考快与慢",
        description="倾向于注意、搜索和回忆支持自己既有信念的信息，忽略或贬低相反证据。",
        detection_hint="检查是否只关注支持自身立场的信息，对反面证据视而不见",
        keywords=["我当然", "我一直", "正如我所料", "果然不出", "毫无疑问"],
        severity="高"
    ),
    Fallacy(
        id="availability_heuristic",
        chinese_name="可得性启发",
        english_name="Availability Heuristic",
        category="认知偏见", subcategory="启发式判断",
        source_book="思考快与慢",
        description="根据想起具体例子的难易程度来评估事件概率。容易被记住的（戏剧性、最近发生的）被判断为更可能。",
        detection_hint="检查是否基于容易想起的例子而非统计数据来判断概率",
        keywords=["最近", "经常听说", "印象中", "新闻上", "记得有", "身边"],
        severity="中"
    ),
    Fallacy(
        id="representativeness",
        chinese_name="代表性启发",
        english_name="Representativeness Heuristic",
        category="认知偏见", subcategory="启发式判断",
        source_book="思考快与慢",
        description="根据某事物与典型类别的相似程度来判断其归属概率。忽略基础概率，只看'像不像'。",
        detection_hint="检查是否以'像不像'典型来替代概率判断",
        keywords=["典型的", "看起来像", "这种人", "标准案例", "很符合"],
        severity="中"
    ),
    Fallacy(
        id="anchoring",
        chinese_name="锚定效应",
        english_name="Anchoring Effect",
        category="认知偏见", subcategory="判断参照",
        source_book="思考快与慢",
        description="初始信息（锚点）对后续判断产生不成比例的影响。即使锚点与判断无关，仍会吸附判断。",
        detection_hint="检查是否存在一个初始参照值过度影响了最终判断",
        keywords=["锚定", "基准", "起价", "原价", "参考价", "基于此"],
        severity="中"
    ),
    Fallacy(
        id="framing_effect",
        chinese_name="框架效应",
        english_name="Framing Effect",
        category="认知偏见", subcategory="决策偏差",
        source_book="思考快与慢",
        description="同一问题以不同方式（获益框架/损失框架）表述时，人们做出不同的决策。",
        detection_hint="检查同一问题是否被以不同框架表述并引导特定决策",
        keywords=["损失", "收益", "存活率", "死亡率", "概率"],
        severity="中"
    ),
    Fallacy(
        id="loss_aversion",
        chinese_name="损失厌恶",
        english_name="Loss Aversion",
        category="认知偏见", subcategory="决策偏差",
        source_book="思考快与慢",
        description="同等程度的损失比收益带来的心理冲击更大（约2倍）。人们为避免损失宁愿承担更多风险。",
        detection_hint="检查是否对损失的担忧远超对收益的期待",
        keywords=["舍不得", "放弃太可惜", "难以割舍", "白费了", "不能白花"],
        severity="中"
    ),
    Fallacy(
        id="sunk_cost",
        chinese_name="沉没成本谬误",
        english_name="Sunk Cost Fallacy",
        category="认知偏见", subcategory="决策偏差",
        source_book="思考快与慢",
        description="因已经投入了无法收回的成本（时间/金钱/精力），而继续坚持一个不再合理的决策。",
        detection_hint="检查是否因为'已经投入了这么多'而坚持错误的选择",
        keywords=["已经投入", "白费", "不能半途而废", "坚持到现在", "已经花了"],
        severity="高"
    ),
    Fallacy(
        id="overconfidence",
        chinese_name="过度自信",
        english_name="Overconfidence Effect",
        category="认知偏见", subcategory="元认知偏差",
        source_book="思考快与慢",
        description="高估自己的知识、判断能力和预测准确性，尤其在面对不确定问题时。",
        detection_hint="检查是否在没有充分证据的情况下给出了过于确定的断言",
        keywords=["毫无疑问", "绝对正确", "100%", "一定", "必然", "绝不可能", "绝对"],
        severity="中"
    ),
    Fallacy(
        id="hindsight_bias",
        chinese_name="事后聪明偏差",
        english_name="Hindsight Bias (I-Knew-It-All-Along)",
        category="认知偏见", subcategory="记忆偏差",
        source_book="思考快与慢",
        description="事后认为自己'早就知道'结果会是这样，低估了事前预测的难度。",
        detection_hint="检查是否在事后表现得好像结果从一开始就是显而易见的",
        keywords=["早就知道", "早该", "预料之中", "不出所料", "果然"],
        severity="低"
    ),
    Fallacy(
        id="halo_effect",
        chinese_name="光环效应",
        english_name="Halo Effect",
        category="认知偏见", subcategory="社会认知",
        source_book="思考快与慢",
        description="对某人/物在某方面的正面印象泛化到其他方面。一好百好，以偏概全。",
        detection_hint="检查是否因某一突出的正面特征而忽视了其他方面的评估",
        keywords=["各方面都", "完美", "全面", "无一不"],
        severity="中"
    ),
    Fallacy(
        id="planning_fallacy",
        chinese_name="规划谬误",
        english_name="Planning Fallacy",
        category="认知偏见", subcategory="预测偏差",
        source_book="思考快与慢",
        description="系统性地低估完成任务所需的时间/成本/风险，高估收益。",
        detection_hint="检查是否对项目的时间/成本/风险评估过于乐观",
        keywords=["按时完成", "预算内", "乐观估计", "很快就能", "赶得上"],
        severity="中"
    ),
    Fallacy(
        id="optimism_bias",
        chinese_name="乐观偏差",
        english_name="Optimism Bias",
        category="认知偏见", subcategory="预测偏差",
        source_book="思考快与慢",
        description="认为负面的情况更可能发生在别人身上而非自己身上。自己永远幸运，别人才会倒霉。",
        detection_hint="检查是否认为'自己''我们'比'别人''他们'更不容易遭遇负面的情况",
        keywords=["应该没问题", "不会发生在我", "我运气好", "不至于", "别人会"],
        severity="中"
    ),
    Fallacy(
        id="endowment_effect",
        chinese_name="禀赋效应",
        english_name="Endowment Effect",
        category="认知偏见", subcategory="所有权偏差",
        source_book="思考快与慢",
        description="一旦拥有某物，对其估值会显著高于未拥有时。'我的'就是更好的。",
        detection_hint="检查是否因'已经拥有'而对某物的价值评价偏高",
        keywords=["我的", "我拥有的", "舍不得卖", "自己的"],
        severity="低"
    ),
    Fallacy(
        id="status_quo_bias",
        chinese_name="现状偏好",
        english_name="Status Quo Bias",
        category="认知偏见", subcategory="决策偏差",
        source_book="思考快与慢",
        description="倾向于维持现有状态，不愿意改变。损失厌恶的一种表现——改变的潜在损失被高估。",
        detection_hint="检查是否以'保持现状''不变'作为理由，而非评估当前和替代方案本身的优劣",
        keywords=["一直以来", "保持不变", "维持现状", "不改变", "习惯"],
        severity="低"
    ),
    Fallacy(
        id="fundamental_attribution",
        chinese_name="基本归因错误",
        english_name="Fundamental Attribution Error",
        category="认知偏见", subcategory="社会认知",
        source_book="思考快与慢",
        description="解释他人行为时过分强调内在特质而低估外部情境因素。自己犯错是环境所迫，别人犯错是人品使然。",
        detection_hint="检查是否将他人的行为更多归因于人品/性格而非情境因素",
        keywords=["他就是", "他就是那种人", "本性如此", "素质差"],
        severity="中"
    ),
    Fallacy(
        id="dunning_kruger",
        chinese_name="达克效应",
        english_name="Dunning-Kruger Effect",
        category="认知偏见", subcategory="元认知偏差",
        source_book="思考快与慢",
        description="能力低的人高估自己，能力高的人低估自己。无知者不知道自己无知。",
        detection_hint="检查是否在明显缺乏专业知识的情况下表现出过度自信",
        keywords=["这么简单", "没什么难的", "不就是"],
        severity="中"
    ),
    Fallacy(
        id="groupthink",
        chinese_name="群体思维",
        english_name="Groupthink",
        category="认知偏见", subcategory="社会认知",
        source_book="思考快与慢",
        description="群体中为追求一致而压制异议，导致决策质量下降。异议不被鼓励，批判性思考被搁置。",
        detection_hint="检查是否用'所有人一致认为'来压制不同意见",
        keywords=["大家都同意", "一致认为", "没有异议", "全体通过"],
        severity="高"
    ),
    Fallacy(
        id="selective_perception",
        chinese_name="选择性知觉",
        english_name="Selective Perception",
        category="认知偏见", subcategory="信息处理",
        source_book="思考快与慢",
        description="人们倾向于以符合自己期望和信念的方式感知信息，过滤掉不一致的信息。",
        detection_hint="检查是否先入为主地解读了模糊信息以符合自己的期望",
        keywords=["只看到", "选择性地", "自动过滤"],
        severity="中"
    ),
    Fallacy(
        id="false_consensus",
        chinese_name="虚假共识",
        english_name="False Consensus Effect",
        category="认知偏见", subcategory="社会认知",
        source_book="思考快与慢",
        description="高估他人与自己在观点/行为上的一致程度。认为'我的看法是大多数人的看法'。",
        detection_hint="检查是否暗含'大家都这么想/做'但实际依据不足",
        keywords=["大家都会", "正常人都", "有常识的人", "任何一个人都"],
        severity="中"
    ),
]

# ========================================================================
# 第六部分：论证规则违反 — Argumentation Rule Violations (Weston)
# 违反《论证是一门学问》50条论证规则
# 来源：《论证是一门学问》
# ========================================================================

ARGUMENTATION_VIOLATIONS = [
    Fallacy(
        id="no_clear_conclusion",
        chinese_name="结论不明确",
        english_name="No Clear Conclusion",
        category="论证规则违反", subcategory="结构规则",
        source_book="论证是一门学问",
        description="结论没有明确陈述，读者不知道论证的终点在哪里。",
        detection_hint="检查是否没有用'所以''因此'等结论标记词来标明论证的结论",
        keywords=[],
        severity="中"
    ),
    Fallacy(
        id="no_clear_premise",
        chinese_name="前提不明确",
        english_name="No Clear Premise",
        category="论证规则违反", subcategory="结构规则",
        source_book="论证是一门学问",
        description="没有明确给出理由或前提，只有结论。读者不知道论据是什么。",
        detection_hint="检查是否没有用'因为''由于'等前提标记词来标明支持结论的理由",
        keywords=[],
        severity="中"
    ),
    Fallacy(
        id="unreliable_premise",
        chinese_name="前提不可靠",
        english_name="Unreliable Premise",
        category="论证规则违反", subcategory="前提要求",
        source_book="论证是一门学问",
        description="前提本身不真实、不可接受或缺乏证据支持。从不可靠前提出发无法建立可靠论证。",
        detection_hint="检查前提是否真实可靠，有无证据支撑",
        keywords=[],
        severity="高"
    ),
    Fallacy(
        id="vague_language",
        chinese_name="语言模糊/不具体",
        english_name="Vague / Abstract Language",
        category="论证规则违反", subcategory="表达要求",
        source_book="论证是一门学问",
        description="使用了大量模糊抽象词，导致论证无法被准确评估。",
        detection_hint="检查是否有大量'很多''大量''若干'等模糊量词",
        keywords=["很多", "大量", "若干", "一些", "某些"],
        severity="低"
    ),
    Fallacy(
        id="emotional_manipulation",
        chinese_name="诱导性/情感化语言",
        english_name="Emotional / Loaded Language",
        category="论证规则违反", subcategory="表达要求",
        source_book="论证是一门学问",
        description="用情绪化、诱导性的语言替代平实的事实陈述。",
        detection_hint="检查是否使用了带有强烈情感色彩的词汇而非中性描述",
        keywords=["太可怕", "令人发指", "极端", "可恶", "伟大"],
        severity="中"
    ),
    Fallacy(
        id="inconsistent_terms",
        chinese_name="术语前后不一致",
        english_name="Inconsistent Terminology",
        category="论证规则违反", subcategory="表达要求",
        source_book="论证是一门学问",
        description="同一关键术语在论证中不同地方使用了不同含义或不同表述。",
        detection_hint="检查同一关键概念在全文不同位置是否保持相同含义",
        keywords=[],
        severity="中"
    ),
    Fallacy(
        id="unrepresentative_example",
        chinese_name="例子不具代表性",
        english_name="Unrepresentative Example",
        category="论证规则违反", subcategory="举例论证",
        source_book="论证是一门学问",
        description="举例论证时使用的例子不具有代表性，不能代表其所声称的类别。",
        detection_hint="检查所举例子是否能代表其所要说明的一般情况",
        keywords=["例如", "比如", "举例"],
        severity="中"
    ),
    Fallacy(
        id="ignored_counterexample",
        chinese_name="忽视反面例证",
        english_name="Ignored Counterexample",
        category="论证规则违反", subcategory="举例论证",
        source_book="论证是一门学问",
        description="在进行概括性论证时，存在明显的反例但被忽略或未加讨论。",
        detection_hint="检查是否存在与概括结论矛盾但未被讨论的明显反例",
        keywords=["反例", "例外", "相反的例子"],
        severity="高"
    ),
    Fallacy(
        id="authority_out_of_field",
        chinese_name="权威不在相关领域",
        english_name="Authority Outside Their Field",
        category="论证规则违反", subcategory="诉诸权威",
        source_book="论证是一门学问",
        description="引用的权威人士或机构不在其所讨论的专业领域内。",
        detection_hint="检查引用的权威是否在相关领域有专业资质",
        keywords=[],
        severity="中"
    ),
    Fallacy(
        id="authority_no_consensus",
        chinese_name="权威意见缺乏共识",
        english_name="Authority Without Consensus",
        category="论证规则违反", subcategory="诉诸权威",
        source_book="论证是一门学问",
        description="引用的权威意见在该领域内存在较大争议，并非学术共识。",
        detection_hint="检查引用的权威意见在该领域是否被广泛接受",
        keywords=[],
        severity="中"
    ),
    Fallacy(
        id="causal_no_mechanism",
        chinese_name="因果论证缺机制",
        english_name="Causal Argument Without Mechanism",
        category="论证规则违反", subcategory="因果论证",
        source_book="论证是一门学问",
        description="主张因果关系但没有解释因果机制，只说'因为A，所以B'而不说明A如何导致B。",
        detection_hint="检查是否声称了因果关系但没有解释连接A和B的作用机制",
        keywords=[],
        severity="中"
    ),
    Fallacy(
        id="causal_no_alternative",
        chinese_name="未考虑替代原因",
        english_name="No Consideration of Alternative Causes",
        category="论证规则违反", subcategory="因果论证",
        source_book="论证是一门学问",
        description="建立因果关系时没有考虑和排除可能的替代解释。一种关联可能有多种原因。",
        detection_hint="检查在论证因果关系时是否排除了其他可能的原因",
        keywords=[],
        severity="中"
    ),
    Fallacy(
        id="single_example_generalization",
        chinese_name="单例概括",
        english_name="Single Example Generalization",
        category="论证规则违反", subcategory="举例论证",
        source_book="论证是一门学问",
        description="仅基于一个例子就做出一般性概括。单个案例不足以支持普遍结论。",
        detection_hint="检查是否仅凭一个例子就推出了一个概括性结论",
        keywords=["一个例子", "有一次", "曾经有一次"],
        severity="高"
    ),
]

# ========================================================================
# 第七部分：非逻辑思维根源 — Non-Logical Roots (McInerny)
# 思维准备阶段的根本性偏差
# 来源：《简单的逻辑学》
# ========================================================================

NON_LOGICAL_ROOTS = [
    Fallacy(
        id="extreme_skepticism",
        chinese_name="极端怀疑论",
        english_name="Extreme Skepticism",
        category="非逻辑思维根源", subcategory="态度障碍",
        source_book="简单的逻辑学",
        description="彻底否认一切真理的可能性，声称'没有真相'或'什么都不确定'。这种立场自相矛盾。",
        detection_hint="检查是否存在否认一切真理可能性的极端表述",
        keywords=["没有真相", "无所谓真假", "什么都不确定"],
        severity="高"
    ),
    Fallacy(
        id="cynicism",
        chinese_name="玩世不恭/犬儒主义",
        english_name="Cynicism",
        category="非逻辑思维根源", subcategory="态度障碍",
        source_book="简单的逻辑学",
        description="预设性地否定别人论证的真实性和价值，'全是假的/骗人的'。未分析即下否定结论。",
        detection_hint="检查是否在未分析之前就先验地否定一切",
        keywords=["全都是假的", "都是骗人的", "全是套路", "没一个好东西"],
        severity="高"
    ),
    Fallacy(
        id="narrow_mindedness",
        chinese_name="眼界狭窄",
        english_name="Narrow-Mindedness",
        category="非逻辑思维根源", subcategory="态度障碍",
        source_book="简单的逻辑学",
        description="自我设限，拒绝考虑其他可能性。'不可能''别无选择'等封闭性表述。",
        detection_hint="检查是否过早关闭了探索其他可能性的空间",
        keywords=["不可能", "绝对不行", "别无选择", "只能这样", "想都别想"],
        severity="中"
    ),
    Fallacy(
        id="emotional_clouding",
        chinese_name="情感遮蔽",
        english_name="Emotional Clouding",
        category="非逻辑思维根源", subcategory="情绪干扰",
        source_book="简单的逻辑学",
        description="强烈情绪（愤怒、悲伤、兴奋）干扰了理性判断能力，使论证偏向情感而非逻辑。",
        detection_hint="检查是否存在大量情绪化宣泄而少有理性论证",
        keywords=["我气就气在", "我受不了", "太可恶", "太可恨"],
        severity="中"
    ),
    Fallacy(
        id="argument_as_combat",
        chinese_name="论证异化为争吵",
        english_name="Argument as Combat",
        category="非逻辑思维根源", subcategory="态度障碍",
        source_book="简单的逻辑学",
        description="将论证的目的从寻求真理转变为击败对手。以'赢'为目标的对话失去了探寻意义。",
        detection_hint="检查是否以击败对方而非探寻真理为目标",
        keywords=["你输了", "我赢了", "你错了", "你根本不懂"],
        severity="中"
    ),
    Fallacy(
        id="sincerity_fallacy",
        chinese_name="真诚陷阱",
        english_name="Sincerity Fallacy",
        category="非逻辑思维根源", subcategory="认知误区",
        source_book="简单的逻辑学",
        description="认为诚实的信念就等于正确的论证。'我坚信'并不等于'这是真的'。",
        detection_hint="检查是否用'我相信''我坚信'来代替论证",
        keywords=["我坚信", "我深信", "我凭良心说"],
        severity="中"
    ),
    Fallacy(
        id="fact_opinion_confusion",
        chinese_name="事实与观点混淆",
        english_name="Fact-Opinion Confusion",
        category="非逻辑思维根源", subcategory="认知误区",
        source_book="简单的逻辑学",
        description="把主观观点当作客观事实来陈述，或者把事实当作观点来相对化。",
        detection_hint="检查是否把应该用证据支撑的事实性主张当作个人观点来处理",
        keywords=["我觉得", "我认为", "在我看来"],
        severity="中"
    ),
    Fallacy(
        id="cognitive_dissonance",
        chinese_name="认知失调",
        english_name="Cognitive Dissonance",
        category="非逻辑思维根源", subcategory="心理障碍",
        source_book="学会提问",
        description="新证据与既有信念冲突时产生不适感，为减轻不适而合理化/否认新证据。",
        detection_hint="检查面对矛盾证据时是否采用合理化而非重新审视立场的态度",
        keywords=["但这不一样", "这个情况特殊", "不能一概而论"],
        severity="低"
    ),
]

# ========================================================================
# 第八部分：结构化谬误 — Structural Fallacies (McKinsey)
# 违反MECE/金字塔/逻辑树原则的思维错误
# 来源：《麦肯锡教我的逻辑思维》
# ========================================================================

STRUCTURAL_FALLACIES = [
    Fallacy(
        id="non_mece",
        chinese_name="不MECE/分类重叠遗漏",
        english_name="Non-MECE Classification",
        category="结构化谬误", subcategory="分类谬误",
        source_book="麦肯锡逻辑思维",
        description="分类时不相互独立(Mutually Exclusive)或没有完全穷尽(Collectively Exhaustive)。导致分析框架有漏洞或重复。",
        detection_hint="检查分类维度的各选项之间是否有重叠或遗漏",
        keywords=["分为", "分类", "类别", "方面"],
        severity="中"
    ),
    Fallacy(
        id="no_pyramid",
        chinese_name="金字塔结构缺失",
        english_name="Missing Pyramid Structure",
        category="结构化谬误", subcategory="层次谬误",
        source_book="麦肯锡逻辑思维",
        description="论述缺乏自上而下的金字塔结构：结论不在顶层，论据不按层次组织。",
        detection_hint="检查是否先给出结论然后分层展开，还是杂乱堆砌",
        keywords=[],
        severity="低"
    ),
    Fallacy(
        id="mixed_levels",
        chinese_name="混层/层次混淆",
        english_name="Mixed Levels of Abstraction",
        category="结构化谬误", subcategory="层次谬误",
        source_book="麦肯锡逻辑思维",
        description="在同一层次的论述中混入了不同抽象层级的内容。如把具体操作和战略原则混为一谈。",
        detection_hint="检查同一层次的论述是否保持了同等的抽象程度",
        keywords=["宏观", "微观", "战略", "具体", "细节"],
        severity="中"
    ),
    Fallacy(
        id="logical_tree_broken",
        chinese_name="逻辑树断裂",
        english_name="Broken Logic Tree",
        category="结构化谬误", subcategory="分解谬误",
        source_book="麦肯锡逻辑思维",
        description="问题分解的某个分支无法支撑上一层的结论，或分支之间缺乏逻辑关联。",
        detection_hint="检查各项分解是否都能支撑上一层的结论",
        keywords=[],
        severity="中"
    ),
    Fallacy(
        id="false_priority",
        chinese_name="虚假优先级",
        english_name="False Priority",
        category="结构化谬误", subcategory="优先序谬误",
        source_book="麦肯锡逻辑思维",
        description="在未做系统分析之前就断言某项是最重要/最紧急的。",
        detection_hint="检查是否在没有评估其他选项的情况下就断言某项是'最重要'的",
        keywords=["最重要", "最关键", "首要任务", "首先需要"],
        severity="中"
    ),
    Fallacy(
        id="quadrant_confusion",
        chinese_name="象限误置",
        english_name="Quadrant Misplacement",
        category="结构化谬误", subcategory="框架谬误",
        source_book="麦肯锡逻辑思维",
        description="在使用四象限等分析框架时，将事物放入了错误的象限，导致分析结论偏差。",
        detection_hint="检查分析框架中各项的定位是否合理",
        keywords=["象限", "矩阵", "二维"],
        severity="低"
    ),
    Fallacy(
        id="analysis_paralysis",
        chinese_name="分析瘫痪",
        english_name="Analysis Paralysis",
        category="结构化谬误", subcategory="过程谬误",
        source_book="麦肯锡逻辑思维",
        description="过度分析导致无法做出决策。不断分解问题但永远不到得出结论的阶段。",
        detection_hint="检查是否在分析上花费了过多精力但迟迟没有结论",
        keywords=["还需要更多", "再分析", "还不够"],
        severity="低"
    ),
]

# ========================================================================
# 第九部分：辩证谬误 — Dialectical Fallacies (Harvey)
# 违反辩证系统分析原则的思维错误
# 来源：《世界的逻辑》
# ========================================================================

DIALECTICAL_FALLACIES = [
    Fallacy(
        id="static_thinking",
        chinese_name="静态思维/忽略历史动态",
        english_name="Static Thinking (Ignoring Historical Dynamics)",
        category="辩证谬误", subcategory="过程谬误",
        source_book="世界的逻辑",
        description="将当前状态视为固定不变，忽略了事物发展的历史过程和内在矛盾驱动的变化。",
        detection_hint="检查是否将当前状态当作永恒不变，没有考虑历史发展过程",
        keywords=["一直如此", "永远都是", "从来", "历来"],
        severity="中"
    ),
    Fallacy(
        id="ignored_contradiction",
        chinese_name="无视内在矛盾",
        english_name="Ignored Internal Contradiction",
        category="辩证谬误", subcategory="矛盾谬误",
        source_book="世界的逻辑",
        description="忽略了系统内部固有的矛盾和张力，而这些矛盾恰恰是变化的驱动力。",
        detection_hint="检查是否将系统描述为完全和谐统一，忽略了内部冲突",
        keywords=["没有任何矛盾", "完美统一", "完全一致"],
        severity="中"
    ),
    Fallacy(
        id="binary_dialectics",
        chinese_name="二元辩证/简化对立",
        english_name="Binary Dialectics (Over-Simplified Opposition)",
        category="辩证谬误", subcategory="矛盾谬误",
        source_book="世界的逻辑",
        description="把复杂的辩证对立简化为非此即彼的二元对立，忽略了多层次的交互关系。",
        detection_hint="检查是否把复杂的对立关系简化成了单纯的二元对立",
        keywords=["对立", "对抗", "势不两立"],
        severity="低"
    ),
    Fallacy(
        id="ignored_totality",
        chinese_name="忽视整体性/系统孤立",
        english_name="Ignored Totality (Isolated Analysis)",
        category="辩证谬误", subcategory="系统谬误",
        source_book="世界的逻辑",
        description="将部分从整体系统中孤立出来分析，忽略了部分与整体的相互作用。",
        detection_hint="检查是否孤立地分析个别因素而忽略了其在更大系统中的位置和作用",
        keywords=["单独", "孤立地", "与其他无关"],
        severity="中"
    ),
    Fallacy(
        id="linear_oversimplify",
        chinese_name="线性简化/忽略复杂性",
        english_name="Linear Oversimplification",
        category="辩证谬误", subcategory="系统谬误",
        source_book="世界的逻辑",
        description="用简单的线性因果关系解释复杂的系统现象，忽略了反馈回路和非线性效应。",
        detection_hint="检查是否用简单的单向因果关系来解释复杂的系统行为",
        keywords=["直线", "线性", "直接导致", "一环扣一环"],
        severity="中"
    ),
    Fallacy(
        id="spatial_fixation",
        chinese_name="空间固定/忽视空间维度",
        english_name="Spatial Fixation",
        category="辩证谬误", subcategory="空间谬误",
        source_book="世界的逻辑",
        description="分析社会现象时忽略了地理/空间维度和地点特定的因素。",
        detection_hint="检查是否忽略了空间/地理/位置因素对分析对象的影响",
        keywords=["在哪里都一样", "不分地方", "不分地域"],
        severity="低"
    ),
]

# ========================================================================
# 第十部分：源思维谬误 — Source Thinking Fallacies (何艳玲)
# 认知深度和思维层次的谬误
# 来源：《源思维》
# ========================================================================

SOURCE_THINKING_FALLACIES = [
    Fallacy(
        id="fact_phenomenon_confusion",
        chinese_name="事实与现象混淆",
        english_name="Fact-Phenomenon Confusion",
        category="源思维谬误", subcategory="还原事实",
        source_book="源思维",
        description="未区分原始事实和已被诠释的现象，将经过加工的'现象'当作纯客观'事实'。",
        detection_hint="检查是否把已经被诠释/加工过的信息当作了原始事实",
        keywords=["事实是", "实际上", "本质上"],
        severity="中"
    ),
    Fallacy(
        id="surface_only",
        chinese_name="停留表象/缺乏深度",
        english_name="Staying at the Surface",
        category="源思维谬误", subcategory="还原事实",
        source_book="源思维",
        description="只看到表面现象，没有深入挖掘背后的结构性因素和深层逻辑。",
        detection_hint="检查是否停留在表面描述而没有向下追问深层次原因",
        keywords=["表面上", "看起来", "显而易见"],
        severity="中"
    ),
    Fallacy(
        id="single_cause_thinking",
        chinese_name="归因单因/不辨多元因果",
        english_name="Single Cause Attribution",
        category="源思维谬误", subcategory="辨析因果",
        source_book="源思维",
        description="将复杂结果归因于单一因素，没有识别出多元因果网络中的作用。",
        detection_hint="检查是否把复杂结果简单归因于一个原因",
        keywords=["就是因为", "唯一的理由是", "根子在于"],
        severity="中"
    ),
    Fallacy(
        id="superficial_causality",
        chinese_name="表层因果/未溯因",
        english_name="Superficial Causality",
        category="源思维谬误", subcategory="辨析因果",
        source_book="源思维",
        description="找到了某层因果关系就停止追问，没有继续深入追索更深层的结构性原因。",
        detection_hint="检查是否在找到一个表层原因后就停止了追问'为什么'",
        keywords=["原因是", "因为", "所以"],
        severity="低"
    ),
    Fallacy(
        id="wrong_incision",
        chinese_name="切口错误/锚定失准",
        english_name="Wrong Incision (Mis-Anchoring)",
        category="源思维谬误", subcategory="锚定切口",
        source_book="源思维",
        description="分析问题的切入点（切口）选择错误，导致后续分析偏离了真正关键的问题。",
        detection_hint="检查分析的切入点是否是真正解决该问题的关键杠杆点",
        keywords=["突破口", "切入点", "关键", "抓手"],
        severity="高"
    ),
    Fallacy(
        id="level_confusion",
        chinese_name="层次混淆/诊断错层",
        english_name="Level Confusion in Diagnosis",
        category="源思维谬误", subcategory="层次诊断",
        source_book="源思维",
        description="将不同层次的问题（个人/制度/文化/结构）混为一谈，用低层次的解决方案应对高层次问题。",
        detection_hint="检查是否混淆了个人、制度、文化、结构等不同层次的问题",
        keywords=["个人", "制度", "文化", "结构", "系统"],
        severity="中"
    ),
    Fallacy(
        id="dichotomous_source",
        chinese_name="非此即彼式溯源",
        english_name="Dichotomous Source Tracing",
        category="源思维谬误", subcategory="还原事实",
        source_book="源思维",
        description="将复杂问题的成因简化为两个对立因素的竞争，忽略了其他可能的解释维度。",
        detection_hint="检查是否把问题溯源简化为两个对立因素的较量",
        keywords=["要么是", "要不是", "二者必居其一"],
        severity="低"
    ),
]

# ========================================================================
# 最终注册表
# ========================================================================

FALLACY_REGISTRY: list[Fallacy] = (
    FORMAL_FALLACIES +
    AMBIGUITY_FALLACIES +
    RELEVANCE_FALLACIES +
    PRESUMPTION_FALLACIES +
    COGNITIVE_BIASES +
    ARGUMENTATION_VIOLATIONS +
    NON_LOGICAL_ROOTS +
    STRUCTURAL_FALLACIES +
    DIALECTICAL_FALLACIES +
    SOURCE_THINKING_FALLACIES
)

# 分类索引
CATEGORY_INDEX: dict[str, list[Fallacy]] = {}
for f in FALLACY_REGISTRY:
    CATEGORY_INDEX.setdefault(f.category, []).append(f)

# 来源书籍索引
BOOK_INDEX: dict[str, list[Fallacy]] = {}
for f in FALLACY_REGISTRY:
    BOOK_INDEX.setdefault(f.source_book, []).append(f)


def get_fallacies_by_category(category: str) -> list[Fallacy]:
    """按分类获取谬误列表"""
    return CATEGORY_INDEX.get(category, [])


def get_fallacies_by_book(book: str) -> list[Fallacy]:
    """按来源书籍获取谬误列表"""
    return BOOK_INDEX.get(book, [])


def match_keyword_fallacies(text: str, category_filter: Optional[list[str]] = None) -> list[Fallacy]:
    """用关键词匹配检测文本中的已知谬误（规则引擎使用）

    返回所有至少有一个关键词命中的 Fallacy 对象。
    注意：关键词匹配只能检测到关键词明确出现的谬误，
    无法覆盖需要语义理解的类型（留待 LLM 处理）。

    Args:
        text: 待分析文本
        category_filter: 可选，只返回指定分类的谬误（如 ["形式谬误", "关联性谬误"]）
    """
    matched = []
    seen_ids = set()
    for f in FALLACY_REGISTRY:
        if f.id in seen_ids:
            continue
        if category_filter and f.category not in category_filter:
            continue
        for kw in f.keywords:
            if kw and kw in text:
                matched.append(f)
                seen_ids.add(f.id)
                break
    return matched


def match_name_fallacies(text: str, category_filter: Optional[list[str]] = None) -> list[Fallacy]:
    """通过谬误中文名精确子串匹配检测（专供规则引擎使用）

    只检查 Fallacy.chinese_name 是否出现在文本中，避免 match_keyword_fallacies
    中宽泛关键词导致的误报。同时处理 "/" 分隔的别名。

    Args:
        text: 待分析文本
        category_filter: 可选，只返回指定分类的谬误
    """
    matched = []
    seen_ids = set()
    for f in FALLACY_REGISTRY:
        if f.id in seen_ids:
            continue
        if category_filter and f.category not in category_filter:
            continue
        # 检查完整中文名
        if f.chinese_name and f.chinese_name in text:
            matched.append(f)
            seen_ids.add(f.id)
            continue
        # 检查 "/" 分隔的别名（如 "诉诸嘲笑/以笑饰非" → 分别检查）
        for alias in f.chinese_name.split("/"):
            alias = alias.strip()
            if alias and len(alias) >= 2 and alias in text:
                matched.append(f)
                seen_ids.add(f.id)
                break
    return matched


def build_llm_fallacy_taxonomy_prompt(category_filter: Optional[list[str]] = None) -> str:
    """为 LLM 构建完整的谬误分类知识提示

    用于 logic_problem_hunter 和 llm_primary 的 prompt 中，
    让 LLM 能够识别完整的谬误类型体系。
    """
    categories = category_filter or list(CATEGORY_INDEX.keys())

    lines = []
    for cat in categories:
        fallacies = CATEGORY_INDEX.get(cat, [])
        if not fallacies:
            continue
        lines.append(f"\n### {cat}")
        for f in fallacies:
            hint = f" — {f.detection_hint}" if f.detection_hint else ""
            lines.append(f"- **{f.chinese_name}** ({f.english_name}){hint}")

    return "\n".join(lines)


def count_fallacies() -> dict:
    """返回各分类的谬误数量统计"""
    return {cat: len(items) for cat, items in sorted(CATEGORY_INDEX.items())}
