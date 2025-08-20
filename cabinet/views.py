from django.shortcuts import render


def dashboard(request):
    return render(request, "cabinet/dashboard.html")


def bills_list(request):
    return render(request, "cabinet/placeholder.html", {"title": "Квитанции — все"})


def bills_paid(request):
    return render(
        request, "cabinet/placeholder.html", {"title": "Квитанции — оплаченные"}
    )


def bills_overdue(request):
    return render(
        request, "cabinet/placeholder.html", {"title": "Квитанции — просроченные"}
    )


def tariffs_active(request):
    return render(
        request, "cabinet/placeholder.html", {"title": "Тарифы — действующие"}
    )


def tariffs_archive(request):
    return render(request, "cabinet/placeholder.html", {"title": "Тарифы — архив"})


def messages_list(request):
    return render(request, "cabinet/placeholder.html", {"title": "Сообщения"})


def service_request(request):
    return render(request, "cabinet/placeholder.html", {"title": "Вызов мастера"})


def profile(request):
    return render(request, "cabinet/placeholder.html", {"title": "Профиль"})
