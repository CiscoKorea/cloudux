from django.shortcuts import render

# Create your views here.


def dashboard(request):
    return render(request, 'dashboard.html', {})


def hosts(request):
    return render(request, 'hostList.html', {})


def vms(request):
    return render(request, 'vmList.html', {})


def vnets(request):
    return render(request, 'virtualNetworkList.html', {})


def volumes(request):
    return render(request, 'volumeList.html', {})


def disks(request):
    return render(request, 'vmDiskList.html', {})


def monitoring(request):
    return render(request, 'Mmonitoring.html', {})


def users(request):
    return render(request, 'userList.html', {})


