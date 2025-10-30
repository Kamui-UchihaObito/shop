from agent.router import IntentRouter


def test_router_detects_voc_intent():
    router = IntentRouter()
    result = router.route("请帮我分析近期的差评评论，看看主要痛点")
    assert result.intent == "VOC_ANALYSIS"
    assert result.confidence > 0.7
