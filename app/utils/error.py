def handle_api_error(error: Exception) -> str:
    error_str = str(error).lower()

    if "insufficient_quota" in error_str:
        return "در حال حاضر امکان پاسخ‌گویی وجود ندارد. لطفا بعدا دوباره تلاش کنید."
    elif "rate_limit" in error_str:
        return "به دلیل محدودیت نرخ درخواست، لطفا کمی صبر کنید و دوباره تلاش کنید."
    elif "vision" in error_str:
        return "مدل انتخاب شده از تصاویر پشتیبانی نمی‌کند. لطفا مدلی با قابلیت بینایی انتخاب کنید."
    else:
        return "خطایی در سیستم رخ داده است. لطفا دوباره تلاش کنید."


def get_default_error_message() -> str:
    return "خطایی رخ داده است. لطفا دوباره تلاش کنید."


def format_error_response(error: Exception) -> tuple[str, bool]:
    return get_default_error_message(), False
