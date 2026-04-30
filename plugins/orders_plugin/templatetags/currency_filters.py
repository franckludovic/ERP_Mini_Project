from django import template

register = template.Library()

@register.filter
def smart_currency(value):
    """
    Format large numbers into K, M, B format.
    Example: 1000 -> 1K, 1000000 -> 1M
    """
    try:
        num = float(value)
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B".replace('.0', '')
        if num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M".replace('.0', '')
        if num >= 1_000:
            return f"{num / 1_000:.1f}K".replace('.0', '')
        return f"{num:.0f}"
    except (ValueError, TypeError):
        return value
