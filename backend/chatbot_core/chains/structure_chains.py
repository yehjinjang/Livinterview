from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.runnables import RunnableLambda
import base64


def load_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def make_vision_prompt(prompt_text: str, image_path: str):
    base64_image = load_image_base64(image_path)
    return [
        SystemMessage(content="You are a helpful interior assistant that can understand room images."),
        HumanMessage(content=[
            {"type": "text", "text": prompt_text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ])
    ]


def build_vision_chain(prompt_text: str):
    return RunnableLambda(lambda vars: ChatOpenAI(model="gpt-4o", temperature=0).invoke(
        make_vision_prompt(prompt_text, vars["image_path"])))


# ── 간략 구조 설명 체인 (Vision 기반) ──
brief_structure_chain = build_vision_chain(
    "Briefly describe the wall color, floor material, and overall tone in one English sentence."
)

# ── 상세 구조 설명 체인 (Vision 기반) ──
detailed_structure_chain = build_vision_chain(
    "Describe the room's structure in as much detail as possible, including:\n- Wallpaper pattern and color\n- Floor material and finish\n- Window locations and sizes\n- Door locations and count\n- Ceiling height and lighting fixtures\n- Any other notable architectural or decorative features"
)
