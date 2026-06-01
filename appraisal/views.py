from django.shortcuts import render


def pmr_list(request):

    return render(
        request,
        "appraisal/list.html"
    )