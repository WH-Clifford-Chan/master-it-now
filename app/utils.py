from flask import render_template, request

def is_mobile():
    ua = request.user_agent.string.lower()
    mobile_keywords = [
        "android",
        "iphone",
        "ipad",
        "ios",
        "mobile",
    ]
    return any(keyword in ua for keyword in mobile_keywords)


def render_platform_template(template, **context):
    platform = "mobile" if is_mobile() else "desktop"
    return render_template(f"{platform}/{template}", **context)