from django.shortcuts import render

def manage_routing(request):
    return render(request, 'transcribe/index.html')