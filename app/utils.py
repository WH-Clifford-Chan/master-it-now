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


def render_platform_template(blueprint_or_template, template=None, **context):
    platform = "mobile" if is_mobile() else "desktop"

    if template is None:
        template = blueprint_or_template
        blueprint = request.blueprint or ""
    else:
        blueprint = blueprint_or_template

    if "/" in template:
        template_path = template
    elif blueprint:
        template_path = f"{blueprint}/{platform}/{template}"
    else:
        template_path = f"{platform}/{template}"

    return render_template(template_path, **context)