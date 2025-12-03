from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm
from django.shortcuts import get_object_or_404
from .models import History

# Create your views here.

#home page
def home(request):
    return render(request,'base/home.html')

#sign up page
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST,request.FILES)
        if form.is_valid():
            user=form.save()
            login(request,user)
            return redirect("dashbord")
    else:
        form=CustomUserCreationForm()
    return render(request,'base/signup.html',{"form":form})

#login page
def login_view(request):
    if request.method == "POST":
        form=AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request,form.get_user())
            return redirect("dashbord")
    else:
        form=AuthenticationForm()
    return render(request,'base/login.html',{"form":form})

#logout
def logout_view(request):
    if request.method =="POST":
        logout(request)
        return redirect("home")

#import grpc

import sys
sys.path.append(r"C:\Users\winsi\Desktop\grpc_first_test") 
import grpc
import plant_pb2
import plant_pb2_grpc
#dahsbord
@login_required
def dashbord(request):
    image_url=None
    result=None
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_url = fs.url(filename)
      #result
                # ---------------- gRPC call ----------------
        try:
            # Connect to the gRPC server
            with grpc.insecure_channel('localhost:50051') as channel:
                #create wahed stuv li kayl3b dor
                #dial remote control l grpc server
                #li hay3tina wahed python object l gae rpc functions
                stub = plant_pb2_grpc.PlantServiceStub(channel)
                #read image bytes
                image_bytes = image.read()
                # create grpc request 
                grpc_request = plant_pb2.PlantRequest(image=image_bytes)
                grpc_response = stub.PredictDisease(grpc_request)

                result = grpc_response.prediction  # the string returned from gRPC
        except Exception as e:
            result = f"gRPC error: {str(e)}"
        # -------------------------------------------

        #hidtory
        History.objects.create(
            user=request.user,
            image=filename,   # File saved by FileSystemStorage
            result=result
        )
        #profile
    profile=request.user.profile
    return render(request,'base/dashbord.html',{"result":result,"image_url": image_url,"profile":profile})


from django.core.paginator import Paginator

@login_required
def history(request):
    items = History.objects.filter(user=request.user)
    profile = request.user.profile

    paginator = Paginator(items, 5)  # 5 history items per page
    page = request.GET.get('page')
    items_page = paginator.get_page(page)

    return render(request, "base/history.html", {
        "items": items_page,
        "profile": profile,
    })



@login_required
def delete_history(request, pk):
    item = get_object_or_404(History, id=pk, user=request.user)
    item.delete()
    return redirect("history")


@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("dashbord")

    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(
        request,
        "base/edit_profile.html",
        {"user_form": user_form, "profile_form": profile_form}
    )

