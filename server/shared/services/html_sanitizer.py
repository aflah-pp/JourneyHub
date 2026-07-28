import bleach
from bleach.css_sanitizer import CSSSanitizer

ALLOWED_TAGS = [
    "p",
    "br",
    "strong",
    "em",
    "u",
    "s",
    "ul",
    "ol",
    "li",
    "blockquote",
    "code",
    "pre",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "a",
    "img",
    "span",
    "div",
    "hr",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "target", "rel", "title"],
    "img": ["src", "alt", "width", "height", "loading"],
    "span": ["style", "class", "id"],
    "div": ["style", "class", "id"],
    "*": ["class", "id", "title"],
}

ALLOWED_STYLES = [
    "color",
    "background-color",
    "font-size",
    "font-weight",
    "text-align",
    "text-decoration",
    "margin",
    "padding",
    "border",
    "border-radius",
    "width",
    "height",
]

ALLOWED_PROTOCOLS = ["http", "https", "mailto", "ftp"]


def sanitize_html(content):
    """
    Sanitize HTML content to prevent XSS attacks.
    Compatible with Bleach v6.0.0+
    """
    if not content:
        return content

    css_sanitizer = CSSSanitizer(
        allowed_css_properties=ALLOWED_STYLES,
    )

    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        css_sanitizer=css_sanitizer,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
        strip_comments=True,
    )


def sanitize_text(content):
    """
    Strip all HTML tags and sanitize text content.
    """
    if not content:
        return content

    sanitized = sanitize_html(content)

    return bleach.clean(sanitized, tags=[], strip=True)
