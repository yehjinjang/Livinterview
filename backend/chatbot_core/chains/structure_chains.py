# chatbot_core/chains/structure_chain.py

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


# ── 간략 구조 설명 체인 ──
brief_structure_prompt = PromptTemplate(
    input_variables=["image_url"],
    template="""
Provide a concise description of the room’s wall color, floor material, and floor color in one English sentence.
Image URL: {image_url}
""".strip()
)

brief_structure_chain = LLMChain(
    llm=ChatOpenAI(model="gpt-4o", temperature=0),
    prompt=brief_structure_prompt
)

# ── 상세 구조 설명 체인 ──
detailed_structure_prompt = PromptTemplate(
    input_variables=["image_url"],
    template="""
Describe the room's structure in as much detail as possible in English, including:
- Wallpaper pattern and color
- Floor material and finish
- Window locations and sizes
- Door locations and count
- Ceiling height and lighting fixtures
- Any other notable architectural or decorative features
Image URL: {image_url}
"""
)

detailed_structure_chain = LLMChain(
    llm=ChatOpenAI(model="gpt-4o", temperature=0),
    prompt=detailed_structure_prompt
)
