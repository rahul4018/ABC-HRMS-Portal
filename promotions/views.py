from django.shortcuts import render


def promotion_list(request):

    return render(
        request,
        'promotions/list.html'
    )