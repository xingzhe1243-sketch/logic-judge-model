from .formal_logic import analyze_formal_logic
from .critical_inquiry import analyze_critical_inquiry
from .biases import analyze_biases
from .argumentation import analyze_argumentation
from .elements_of_thought import analyze_elements_of_thought
from .structured import analyze_structured
from .dialectical import analyze_dialectical
from .source_thinking import analyze_source_thinking
from .simple_logic import analyze_simple_logic
from .llm_primary import build_llm_primary_prompt, analyze_llm_primary
from .logic_problem_hunter import analyze_logic_problems
from .zhihu_expert import analyze_zhihu_expert

# 统一谬误注册表
from ..fallacy_registry import (
    Fallacy, FALLACY_REGISTRY,
    get_fallacies_by_category, get_fallacies_by_book,
    match_keyword_fallacies, match_name_fallacies,
    build_llm_fallacy_taxonomy_prompt, count_fallacies,
)

__all__ = [
    "analyze_formal_logic", "analyze_critical_inquiry", "analyze_biases",
    "analyze_argumentation", "analyze_elements_of_thought", "analyze_structured",
    "analyze_dialectical", "analyze_source_thinking", "analyze_simple_logic",
    "build_llm_primary_prompt", "analyze_llm_primary",
    "analyze_logic_problems",
    "analyze_zhihu_expert",
    "Fallacy", "FALLACY_REGISTRY",
    "get_fallacies_by_category", "get_fallacies_by_book",
    "match_keyword_fallacies", "match_name_fallacies",
    "build_llm_fallacy_taxonomy_prompt", "count_fallacies",
]
